"""Approval policy + service tests (PRD §12)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from clawshop.approval import policy
from clawshop.approval.service import ApprovalService, CapturedChannel, Channel
from clawshop.models import Action, ApprovalRequest, Decision, LineItem, Product, User


def _u(**kw) -> User:
    return User(
        id="u1",
        household_id="hh1",
        name="Test",
        auto_approve_limit=kw.get("limit", 20.0),
        trusted_retailers=kw.get("trusted", {"walmart"}),
    )


def _action(**kw) -> Action:
    return Action(
        kind=kw.get("kind", "checkout"),
        user_id="u1",
        household_id="hh1",
        retailer=kw.get("retailer", "walmart"),
        cost=kw.get("cost", 10.0),
        category=kw.get("category", "grocery"),
        items=kw.get("items", []),
        shipping_address=kw.get("addr"),
        estimated_cost=kw.get("est"),
        perishable=kw.get("perishable", False),
    )


def test_cost_above_limit_requires_approval():
    hits = policy.evaluate(_action(cost=50.0), _u(limit=20.0))
    assert any("cost" in h for h in hits)


def test_under_limit_trusted_no_hits():
    hits = policy.evaluate(_action(cost=5.0), _u())
    assert hits == []


def test_untrusted_retailer_fires():
    hits = policy.evaluate(_action(retailer="kroger"), _u(trusted={"walmart"}))
    assert any("retailer" in h for h in hits)


def test_sensitive_category_fires():
    hits = policy.evaluate(_action(cost=5.0, category="alcohol"), _u())
    assert any("alcohol" in h for h in hits)


def test_delta_from_estimate_fires():
    hits = policy.evaluate(_action(cost=12.0, est=10.0), _u(limit=100))
    assert any("delta" in h for h in hits)


def test_new_address_fires():
    ctx = policy.PolicyContext(
        now=datetime.now(timezone.utc), seen_addresses={"old@home"}
    )
    hits = policy.evaluate(_action(addr="new@home"), _u(limit=100), ctx)
    assert any("new address" in h for h in hits)


# --- Service ---


async def _run(service: ApprovalService, action: Action, user: User) -> ApprovalRequest:
    return await service.request(action, user)


def test_no_hits_auto_approves():
    chan = CapturedChannel(answer="denied")
    svc = ApprovalService(chan, seen_addresses={"u1@home"})
    req = asyncio.run(_run(svc, _action(cost=5.0, addr="u1@home"), _u(limit=100)))
    assert req.decision == "approved"
    assert chan.captured == []  # never reached the channel


def test_hits_route_through_channel():
    chan = CapturedChannel(answer="approved")
    svc = ApprovalService(chan, seen_addresses={"u1@home"})
    req = asyncio.run(_run(svc, _action(cost=200.0, addr="u1@home"), _u(limit=20)))
    assert req.decision == "approved"
    assert len(chan.captured) == 1
    assert any("cost" in h for h in chan.captured[0].policy_hits)


def test_consume_blocks_replay():
    chan = CapturedChannel(answer="approved")
    svc = ApprovalService(chan, seen_addresses={"u1@home"})
    req = asyncio.run(_run(svc, _action(cost=100), _u(limit=20)))
    svc.consume(req)
    with pytest.raises(ValueError, match="already consumed"):
        svc.consume(req)


def test_consume_rejects_unapproved():
    chan = CapturedChannel(answer="denied")
    svc = ApprovalService(chan, seen_addresses={"u1@home"})
    req = asyncio.run(_run(svc, _action(cost=100), _u(limit=20)))
    with pytest.raises(ValueError, match="not approved"):
        svc.consume(req)


def test_perishable_uses_short_timeout():
    chan = CapturedChannel(answer="approved")
    svc = ApprovalService(chan, seen_addresses={"u1@home"})
    req = asyncio.run(_run(svc, _action(cost=100, perishable=True), _u(limit=20)))
    assert req.timeout_s == 5 * 60


class _NeverAnswer(Channel):
    """Sleeps past the timeout; verifies silence-never-approves (PRD §12.4)."""

    async def deliver(self, request):
        await asyncio.sleep(60)  # would 'approve' if reached, but service times out
        return "approved"


def test_silence_returns_denied():
    """PRD §12.4 — Approval Service enforces timeout → denied."""
    from clawshop.config import SETTINGS, Thresholds

    short = Thresholds(
        default_approval_timeout_s=0,  # immediate timeout
        perishable_approval_timeout_s=0,
    )
    object.__setattr__(SETTINGS, "thresholds", short)
    try:
        chan = _NeverAnswer()
        svc = ApprovalService(chan, seen_addresses={"u1@home"})
        req = asyncio.run(_run(svc, _action(cost=100), _u(limit=20)))
        assert req.decision == "denied"
    finally:
        object.__setattr__(SETTINGS, "thresholds", Thresholds())
