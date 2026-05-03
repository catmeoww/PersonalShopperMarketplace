"""Predicate DSL for watchers. PRD §7.6.

Tiny grammar: pure Python evaluation, no LLM on the hot path.

Supported expressions (one per predicate; combine with ' and '):
    price < 4.00
    price <= 4
    price > 5
    drop_pct >= 15
    drop_pct > 10
    back_in_stock
    deal_tag in [price_drop, clearance]
"""

from __future__ import annotations

import operator
import re
from dataclasses import dataclass
from typing import Callable

from clawshop.models import Product


@dataclass
class PriceState:
    last_price: float | None
    current_price: float
    in_stock: bool
    deal_tags: tuple[str, ...]


_OPS: dict[str, Callable[[float, float], bool]] = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}

_NUM = r"-?\d+(?:\.\d+)?"
_PRICE_RE = re.compile(rf"^\s*price\s*(<=|>=|<|>|==|!=)\s*({_NUM})\s*$")
_DROP_RE = re.compile(rf"^\s*drop_pct\s*(<=|>=|<|>|==|!=)\s*({_NUM})\s*$")
_TAG_RE = re.compile(r"^\s*deal_tag\s+in\s+\[([^\]]+)\]\s*$")
_STOCK_RE = re.compile(r"^\s*back_in_stock\s*$")


class PredicateError(ValueError):
    pass


def _eval_clause(clause: str, state: PriceState) -> bool:
    if m := _PRICE_RE.match(clause):
        op, n = m.group(1), float(m.group(2))
        return _OPS[op](state.current_price, n)

    if m := _DROP_RE.match(clause):
        if state.last_price is None or state.last_price <= 0:
            return False
        drop = (state.last_price - state.current_price) / state.last_price * 100
        op, n = m.group(1), float(m.group(2))
        return _OPS[op](drop, n)

    if m := _TAG_RE.match(clause):
        wanted = {t.strip() for t in m.group(1).split(",")}
        return any(t in wanted for t in state.deal_tags)

    if _STOCK_RE.match(clause):
        return state.in_stock

    raise PredicateError(f"unparsable predicate clause: {clause!r}")


def evaluate(predicate: str, state: PriceState) -> bool:
    """Evaluate the full predicate (AND across ' and ')."""
    parts = [p.strip() for p in re.split(r"\s+and\s+", predicate.strip()) if p.strip()]
    if not parts:
        return False
    return all(_eval_clause(p, state) for p in parts)


def state_from_product(product: Product, *, last_price: float | None) -> PriceState:
    return PriceState(
        last_price=last_price,
        current_price=product.price,
        in_stock=product.in_stock,
        deal_tags=tuple(product.deal_tags),
    )
