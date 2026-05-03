"""Watcher tests — predicate DSL + hot path discipline (PRD §7.6, F5)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from clawshop import llm
from clawshop.models import Product, WatchedItem
from clawshop.watcher import predicate
from clawshop.watcher.predicate import PriceState, evaluate
from clawshop.watcher.runner import should_ping, tick


def _state(price: float, last: float | None = None, *, in_stock=True, tags=()) -> PriceState:
    return PriceState(last_price=last, current_price=price, in_stock=in_stock, deal_tags=tags)


def test_price_threshold_under():
    assert evaluate("price < 5.00", _state(4.99))
    assert not evaluate("price < 5.00", _state(5.00))


def test_drop_pct():
    assert evaluate("drop_pct >= 15", _state(8.50, last=10.00))  # 15% drop
    assert not evaluate("drop_pct >= 15", _state(9.00, last=10.00))  # 10% drop


def test_back_in_stock():
    assert evaluate("back_in_stock", _state(5, in_stock=True))
    assert not evaluate("back_in_stock", _state(5, in_stock=False))


def test_deal_tag_in():
    assert evaluate("deal_tag in [price_drop, clearance]", _state(5, tags=("price_drop",)))
    assert not evaluate("deal_tag in [clearance]", _state(5, tags=("price_drop",)))


def test_compound_and():
    assert evaluate("price < 5 and back_in_stock", _state(4.50, in_stock=True))
    assert not evaluate("price < 5 and back_in_stock", _state(4.50, in_stock=False))


def test_unparsable_raises():
    import pytest

    with pytest.raises(predicate.PredicateError):
        evaluate("nonsense bla", _state(5))


def test_tick_no_llm_when_no_predicate_fires():
    """Hot-path discipline: predicate doesn't fire → no LLM call (PRD F5)."""
    llm.reset_log()
    p = Product(
        sku="X1",
        retailer="kroger",
        title="X",
        price=10.00,
        in_stock=True,
    )
    w = WatchedItem(
        household_id="hh",
        user_id="u",
        sku="X1",
        retailer="kroger",
        predicate="price < 5.00",
        last_seen_price=10.00,
    )
    res = tick([w], {"X1": p})
    assert res.fired == []
    assert llm.call_log() == []  # zero LLM calls


def test_tick_fires_only_after_cooldown_passed():
    p = Product(sku="X1", retailer="kroger", title="X", price=4.50)
    w = WatchedItem(
        household_id="hh",
        user_id="u",
        sku="X1",
        retailer="kroger",
        predicate="price < 5.00",
        cooldown_s=3600,
        last_fired_at=datetime.now(timezone.utc),  # just fired
        last_seen_price=10.00,
    )
    res = tick([w], {"X1": p})
    assert res.fired == []
    assert any("cooldown" in s for s in res.skipped)


def test_should_ping_uses_haiku_gate():
    """Gate is the only LLM call; stub mode returns 'ping' for non-trivial drops."""
    llm.reset_log()
    p = Product(sku="X1", retailer="kroger", title="X", price=8.50, deal_tags=["price_drop"])
    w = WatchedItem(
        household_id="hh",
        user_id="u",
        sku="X1",
        retailer="kroger",
        predicate="drop_pct >= 15",
        last_seen_price=10.00,
    )
    res = tick([w], {"X1": p})
    assert len(res.fired) == 1
    fire = res.fired[0]
    assert should_ping(fire) is True
    log = llm.call_log()
    assert len(log) == 1
    assert log[0].step == "watcher_gate"
