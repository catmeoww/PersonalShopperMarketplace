"""Declarative approval rules. PRD §12.1.

Order-evaluated. Each rule is a pure function over (Action, User, Context) → reason str | None.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from clawshop.config import SENSITIVE_CATEGORIES, SETTINGS
from clawshop.models import Action, User


@dataclass
class PolicyContext:
    now: datetime
    seen_addresses: set[str]  # addresses observed in the last N days


Rule = Callable[[Action, User, PolicyContext], str | None]


def rule_cost(action: Action, user: User, ctx: PolicyContext) -> str | None:
    if action.cost > user.auto_approve_limit:
        return f"cost ${action.cost:.2f} > auto-approve limit ${user.auto_approve_limit:.2f}"
    return None


def rule_trusted_retailer(action: Action, user: User, ctx: PolicyContext) -> str | None:
    if action.retailer and action.retailer not in user.trusted_retailers:
        return f"retailer '{action.retailer}' not in trusted set"
    return None


def rule_sensitive_category(action: Action, user: User, ctx: PolicyContext) -> str | None:
    if action.category in SENSITIVE_CATEGORIES:
        return f"sensitive category '{action.category}' requires explicit approval"
    return None


def rule_delta_from_estimate(action: Action, user: User, ctx: PolicyContext) -> str | None:
    if action.estimated_cost is None or action.estimated_cost == 0:
        return None
    delta = abs(action.cost - action.estimated_cost) / action.estimated_cost
    if delta > SETTINGS.thresholds.delta_from_estimate_pct:
        return (
            f"price delta {delta:.0%} exceeds "
            f"{SETTINGS.thresholds.delta_from_estimate_pct:.0%} threshold"
        )
    return None


def rule_new_shipping_address(action: Action, user: User, ctx: PolicyContext) -> str | None:
    if action.shipping_address and action.shipping_address not in ctx.seen_addresses:
        return f"shipping to new address '{action.shipping_address}'"
    return None


def rule_quiet_hours(action: Action, user: User, ctx: PolicyContext) -> str | None:
    h = ctx.now.hour
    if SETTINGS.thresholds.quiet_hours_start <= h < SETTINGS.thresholds.quiet_hours_end:
        return f"action attempted during quiet hours ({h:02d}:00 local)"
    return None


# PRD §12.1 — order matters; the first match's reason becomes the headline.
ALL_RULES: list[Rule] = [
    rule_cost,
    rule_trusted_retailer,
    rule_sensitive_category,
    rule_delta_from_estimate,
    rule_new_shipping_address,
    rule_quiet_hours,
]


def evaluate(action: Action, user: User, ctx: PolicyContext | None = None) -> list[str]:
    """Return ordered list of reasons that fired. Empty = no approval needed."""
    if ctx is None:
        ctx = PolicyContext(now=datetime.now(timezone.utc), seen_addresses=set())
    hits: list[str] = []
    for rule in ALL_RULES:
        reason = rule(action, user, ctx)
        if reason:
            hits.append(reason)
    return hits


def make_default_context(seen_addresses: set[str] | None = None) -> PolicyContext:
    return PolicyContext(
        now=datetime.now(timezone.utc),
        seen_addresses=seen_addresses or set(),
    )
