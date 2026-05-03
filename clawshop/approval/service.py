"""Approval Service.

PRD §12.2 channel fallback (interface only — single channel in this prototype).
PRD §12.4 timeout default to denied — silence never approves.
PRD §14.2 single-use approval JWTs (here: uuid tokens) marked-consumed before checkout.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Protocol

from clawshop.approval import policy
from clawshop.config import SETTINGS
from clawshop.models import Action, ApprovalRequest, Decision, User

log = logging.getLogger("clawshop.approval")


class Channel(ABC):
    """Pluggable delivery: stdin for prototype; SMS/push later."""

    @abstractmethod
    async def deliver(self, request: ApprovalRequest) -> Decision: ...


class StdinChannel(Channel):
    """CLI prompt with timeout. Input parsed as Y / N / LATER (PRD §6.2)."""

    def __init__(self, prompt_fn=None) -> None:
        self.prompt_fn = prompt_fn or self._default_prompt

    @staticmethod
    def _default_prompt(text: str) -> str:
        return input(text)

    async def deliver(self, request: ApprovalRequest) -> Decision:
        a = request.action
        lines = [
            "",
            "─" * 60,
            f"APPROVAL REQUESTED  ({request.id[:8]})",
            f"  action:   {a.kind}",
            f"  retailer: {a.retailer}",
            f"  total:    ${a.cost:.2f}",
            f"  items:    {len(a.items)}",
        ]
        for li in a.items:
            lines.append(
                f"    - {li.qty}× {li.product.title} "
                f"(${li.product.price:.2f})  {li.rationale}"
            )
        lines.append(f"  why ask:  {'; '.join(request.policy_hits) or '—'}")
        lines.append(f"  timeout:  {request.timeout_s}s → DENIED if no reply")
        lines.append("─" * 60)
        lines.append("Reply Y / N / LATER: ")
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, self.prompt_fn, "\n".join(lines))
        ans = (raw or "").strip().upper()
        if ans == "Y":
            return "approved"
        if ans == "LATER":
            return "later"
        return "denied"


class CapturedChannel(Channel):
    """Test channel: scripted answer + capture of the request shown to user."""

    def __init__(self, answer: Decision = "approved") -> None:
        self.answer = answer
        self.captured: list[ApprovalRequest] = []

    async def deliver(self, request: ApprovalRequest) -> Decision:
        self.captured.append(request)
        return self.answer


class _Clock(Protocol):
    def now(self) -> datetime: ...


class _RealClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class ApprovalService:
    def __init__(
        self,
        channel: Channel,
        *,
        seen_addresses: set[str] | None = None,
        clock: _Clock | None = None,
    ) -> None:
        self.channel = channel
        self.seen_addresses = seen_addresses or set()
        self.clock = clock or _RealClock()
        self._consumed_tokens: set[str] = set()

    def _build(self, action: Action, user: User) -> ApprovalRequest:
        ctx = policy.PolicyContext(now=self.clock.now(), seen_addresses=self.seen_addresses)
        hits = policy.evaluate(action, user, ctx)
        timeout = (
            SETTINGS.thresholds.perishable_approval_timeout_s
            if action.perishable
            else SETTINGS.thresholds.default_approval_timeout_s
        )
        rationale = "; ".join(hits) or "auto-approve threshold not met"
        return ApprovalRequest(
            action=action,
            policy_hits=hits,
            timeout_s=timeout,
            rationale=rationale,
        )

    async def request(self, action: Action, user: User) -> ApprovalRequest:
        req = self._build(action, user)

        # PRD §12.5 / autonomy: if no rule fired AND action is sub-limit, auto-approve.
        if not req.policy_hits:
            req.decision = "approved"
            req.decided_at = self.clock.now()
            log.info("approval.auto-approved id=%s", req.id)
            return req

        try:
            decision = await asyncio.wait_for(
                self.channel.deliver(req), timeout=req.timeout_s
            )
        except asyncio.TimeoutError:
            decision = "denied"  # PRD §12.4 — silence never approves.
        req.decision = decision
        req.decided_at = self.clock.now()
        log.info("approval.decided id=%s decision=%s", req.id, decision)
        return req

    def consume(self, req: ApprovalRequest) -> None:
        """Single-use guard. PRD §14.2 — marked-consumed before checkout."""
        if req.token in self._consumed_tokens:
            raise ValueError(f"approval token {req.token} already consumed (replay)")
        if req.decision != "approved":
            raise ValueError(f"approval id {req.id} not approved (decision={req.decision})")
        self._consumed_tokens.add(req.token)
        req.consumed = True
