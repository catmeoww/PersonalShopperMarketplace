"""Typed data models. See PRD §10."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Flag, auto
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uid() -> str:
    return uuid4().hex


# --- Identity ----------------------------------------------------------------


class Household(BaseModel):
    id: str = Field(default_factory=_uid)
    name: str


class User(BaseModel):
    id: str = Field(default_factory=_uid)
    household_id: str
    name: str
    phone: str | None = None
    auto_approve_limit: float = 0.0  # T1 default per PRD §12.5.
    trusted_retailers: set[str] = Field(default_factory=set)


# --- Memory (PRD §11.1) ------------------------------------------------------


PrefType = Literal[
    "brand",
    "size",
    "dietary",
    "allergy",
    "medical",
    "budget",
    "cadence",
    "schedule",
]


class Preference(BaseModel):
    id: str = Field(default_factory=_uid)
    household_id: str
    user_id: str | None = None  # None = household-shared.
    key: str
    value: Any
    type: PrefType
    confidence: float
    source_turn_id: str
    source: str = "user_turn"
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    ttl_days: int | None = None
    provisional: bool = False
    frozen: bool = False
    version: int = 1


class MemoryItem(BaseModel):
    """Episodic event."""

    id: str = Field(default_factory=_uid)
    household_id: str
    user_id: str | None = None
    ts: datetime = Field(default_factory=_now)
    kind: str  # 'order', 'rejection', 'rating', 'utterance', etc.
    payload: dict[str, Any] = Field(default_factory=dict)
    retailer: str | None = None
    order_id: str | None = None
    source: str = "user_turn"


class SemanticClaim(BaseModel):
    id: str = Field(default_factory=_uid)
    household_id: str
    user_id: str | None = None
    claim: str
    support_count: int = 1
    last_seen: datetime = Field(default_factory=_now)
    confidence: float = 0.5
    provenance: list[str] = Field(default_factory=list)


# --- Retail ------------------------------------------------------------------


class Capabilities(Flag):
    SEARCH = auto()
    GET_PRODUCT = auto()
    BUILD_CART = auto()
    PRICE_CART = auto()
    CHECKOUT = auto()
    CANCEL = auto()


class Product(BaseModel):
    sku: str
    retailer: str
    title: str
    brand: str | None = None
    size: str | None = None
    price: float  # delivered (incl tax+ship estimate). PRD §6.1 / A2.
    in_stock: bool = True
    category: str = "grocery"
    deal_tags: list[str] = Field(default_factory=list)


class LineItem(BaseModel):
    product: Product
    qty: int = 1
    rationale: str = ""  # "why this SKU?" — PRD C4.


class CartProposal(BaseModel):
    id: str = Field(default_factory=_uid)
    household_id: str
    items_by_retailer: dict[str, list[LineItem]]  # retailer -> items
    handoff_retailers: set[str] = Field(default_factory=set)  # Tier D (Amazon)

    @property
    def total(self) -> float:
        return sum(
            li.product.price * li.qty
            for items in self.items_by_retailer.values()
            for li in items
        )

    def total_for(self, retailer: str) -> float:
        return sum(li.product.price * li.qty for li in self.items_by_retailer.get(retailer, []))


class Cart(BaseModel):
    """A retailer-specific cart returned by buildCart."""

    id: str = Field(default_factory=_uid)
    retailer: str
    items: list[LineItem]
    deep_link: str | None = None  # Tier B handoff URL.
    total: float


class Order(BaseModel):
    id: str = Field(default_factory=_uid)
    household_id: str
    user_id: str
    retailer: str
    items: list[LineItem]
    total: float
    status: Literal["placed", "settled", "cancelled", "failed", "handoff"] = "placed"
    payment_token: str | None = None
    approval_id: str | None = None
    created_at: datetime = Field(default_factory=_now)


# --- Watchers (PRD §7.6) -----------------------------------------------------


class WatchedItem(BaseModel):
    id: str = Field(default_factory=_uid)
    household_id: str
    user_id: str
    sku: str
    retailer: str
    predicate: str  # DSL: "price < 4.00", "drop_pct >= 15", "back_in_stock"
    cooldown_s: int = 6 * 3600
    last_fired_at: datetime | None = None
    perishable: bool = False
    last_seen_price: float | None = None


# --- Approval (PRD §12) ------------------------------------------------------


class Action(BaseModel):
    """Anything that crosses the action-surface boundary (PRD §9.2)."""

    id: str = Field(default_factory=_uid)
    kind: Literal["checkout", "subscription_change", "price_drop_buy", "memory_overwrite"]
    user_id: str
    household_id: str
    retailer: str | None = None
    cost: float = 0.0
    category: str = "grocery"
    items: list[LineItem] = Field(default_factory=list)
    shipping_address: str | None = None
    estimated_cost: float | None = None
    perishable: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


Decision = Literal["approved", "denied", "later"]


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=_uid)
    action: Action
    policy_hits: list[str]  # rule names that fired
    timeout_s: int
    token: str = Field(default_factory=_uid)  # single-use, replay-safe (§14.2)
    consumed: bool = False
    decision: Decision | None = None
    decided_at: datetime | None = None
    rationale: str = ""  # presented to user — "why?" (PRD C4)


# --- Payments (PRD §7.5) -----------------------------------------------------


class PaymentToken(BaseModel):
    """Opaque handle. The vault is the only component that resolves to a card."""

    token: str = Field(default_factory=_uid)
    user_id: str
    merchant: str
    cap: float
    expires_at: datetime
    closed: bool = False
