"""Watcher tick. PRD §7.6, F5.

Predicate evaluates in pure Python against cached prices. Only when a
predicate fires AND the cooldown has passed do we wake the LLM (Haiku-tier
"is this worth pinging?" gate). Empty watchlist = zero LLM calls per tick.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from clawshop import llm
from clawshop.models import Product, WatchedItem
from clawshop.watcher.predicate import evaluate, state_from_product

log = logging.getLogger("clawshop.watcher")


@dataclass
class WatcherFire:
    watched: WatchedItem
    product: Product
    drop_pct: float


@dataclass
class TickResult:
    fired: list[WatcherFire] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def tick(
    watches: list[WatchedItem],
    current_prices: dict[str, Product],
    *,
    now: datetime | None = None,
) -> TickResult:
    """Pure-Python evaluation. Returns watches that should escalate to the gate."""
    now = now or datetime.now(timezone.utc)
    result = TickResult()
    for w in watches:
        product = current_prices.get(w.sku)
        if product is None:
            result.skipped.append(f"{w.sku}: no price")
            continue
        if w.last_fired_at and now - w.last_fired_at < timedelta(seconds=w.cooldown_s):
            result.skipped.append(f"{w.sku}: cooldown")
            continue
        state = state_from_product(product, last_price=w.last_seen_price)
        if not evaluate(w.predicate, state):
            continue
        drop_pct = 0.0
        if w.last_seen_price and w.last_seen_price > 0:
            drop_pct = (w.last_seen_price - product.price) / w.last_seen_price * 100
        result.fired.append(WatcherFire(w, product, drop_pct))
    return result


def should_ping(fire: WatcherFire) -> bool:
    """Haiku-tier "is this worth pinging?" gate. PRD §7.6."""
    user = (
        f"watched={fire.watched.sku} title={fire.product.title!r} "
        f"price={fire.product.price:.2f} drop_pct={fire.drop_pct:.1f} "
        f"in_stock={fire.product.in_stock}"
    )
    out = llm.complete(
        "watcher_gate",
        system="You are the price-drop ping gate. Reply only 'ping' or 'skip'. "
        "Skip on noisy or sub-5% drops; ping on material drops or restocks.",
        user=user,
    ).strip().lower()
    log.info("watcher.gate sku=%s decision=%s", fire.watched.sku, out)
    return out == "ping"
