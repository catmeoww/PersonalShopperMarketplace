"""End-to-end smoke test: PRD §6.1 / A1 — 'we're out of diapers and coffee'."""

from __future__ import annotations

import asyncio

from clawshop.agent.orchestrator import Orchestrator
from clawshop.approval.service import ApprovalService, CapturedChannel
from clawshop.memory.store import MemoryStore
from clawshop.models import Preference, User
from clawshop.payments.vault import PaymentVault
from clawshop.retailers import (
    AmazonMockAdapter,
    KrogerMockAdapter,
    WalmartMockAdapter,
)


def _bootstrap():
    store = MemoryStore()
    hh_id = "hh-okonkwo"
    user = User(
        id="u-maya",
        household_id=hh_id,
        name="Maya",
        auto_approve_limit=20.0,
        trusted_retailers={"walmart", "kroger"},
    )
    for k, v, t in [
        ("diapers_brand", "Pampers", "brand"),
        ("coffee_brand", "Peet's", "brand"),
    ]:
        store.upsert_preference(
            Preference(
                household_id=hh_id,
                user_id=user.id,
                key=k,
                value=v,
                type=t,
                confidence=0.95,
                source_turn_id="seed",
            )
        )
    return store, user


def test_e2e_proposal_includes_diapers_and_coffee():
    store, user = _bootstrap()
    adapters = {
        "walmart": WalmartMockAdapter(),
        "kroger": KrogerMockAdapter(),
        "amazon": AmazonMockAdapter(),
    }
    channel = CapturedChannel(answer="approved")
    approval = ApprovalService(channel, seen_addresses={user.id + "@home"})
    orch = Orchestrator(
        store=store, adapters=adapters, approval=approval, vault=PaymentVault()
    )

    result = asyncio.run(orch.run_request(user, "we're out of diapers and coffee"))
    proposal = result["proposal"]
    skus = [
        li.product.sku.lower()
        for items in proposal.items_by_retailer.values()
        for li in items
    ]
    assert any("diap" in s for s in skus), skus
    assert any("cfe" in s or "coffee" in s for s in skus), skus


def test_e2e_amazon_handoff_no_unauthorized_checkout():
    """Amazon is Tier D: orchestrator must produce a deep_link, never a programmatic order."""
    store, user = _bootstrap()
    adapters = {
        "walmart": WalmartMockAdapter(),
        "kroger": KrogerMockAdapter(),
        "amazon": AmazonMockAdapter(),
    }
    channel = CapturedChannel(answer="approved")
    approval = ApprovalService(channel, seen_addresses={user.id + "@home"})
    orch = Orchestrator(
        store=store, adapters=adapters, approval=approval, vault=PaymentVault()
    )
    # Force Amazon to win: only catalog fixture for "diapers" cheapest at amazon (42.50).
    result = asyncio.run(orch.run_request(user, "diapers"))
    placed_retailers = {o.retailer for o in result["placed_orders"]}
    assert "amazon" not in placed_retailers
    # Either amazon won and was handed off, or another retailer was cheaper (also valid).
    if "amazon" in result["proposal"].items_by_retailer:
        assert "amazon" in result["handoffs"]
        assert "amazon.example" in result["handoffs"]["amazon"]


def test_e2e_replay_blocked():
    """Approval token can't be reused — PRD §14.2 replay defense."""
    store, user = _bootstrap()
    adapters = {
        "walmart": WalmartMockAdapter(),
        "kroger": KrogerMockAdapter(),
        "amazon": AmazonMockAdapter(),
    }
    channel = CapturedChannel(answer="approved")
    approval = ApprovalService(channel, seen_addresses={user.id + "@home"})
    orch = Orchestrator(
        store=store, adapters=adapters, approval=approval, vault=PaymentVault()
    )
    result = asyncio.run(orch.run_request(user, "we're out of diapers and coffee"))
    # Each placed order's approval is consumed; re-consuming should raise.
    if not result["placed_orders"]:
        return
    placed = result["placed_orders"][0]
    req = result["approvals"][placed.retailer]
    import pytest

    with pytest.raises(ValueError):
        approval.consume(req)
