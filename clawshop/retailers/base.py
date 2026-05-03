"""Adapter contract every retailer implements. PRD §7.4."""

from __future__ import annotations

from abc import ABC, abstractmethod

from clawshop.models import Cart, Capabilities, LineItem, Order, Product


class RetailerAdapter(ABC):
    name: str

    @abstractmethod
    def capabilities(self) -> Capabilities: ...

    @abstractmethod
    async def search(self, query: str, *, limit: int = 5) -> list[Product]: ...

    @abstractmethod
    async def get_product(self, sku: str) -> Product: ...

    @abstractmethod
    async def build_cart(self, items: list[LineItem]) -> Cart: ...

    @abstractmethod
    async def price_cart(self, cart: Cart) -> Cart: ...

    @abstractmethod
    async def checkout(
        self, cart: Cart, *, payment_token: str, user_id: str, household_id: str
    ) -> Order: ...

    @abstractmethod
    async def get_order(self, order_id: str) -> Order: ...

    @abstractmethod
    async def cancel(self, order_id: str) -> bool: ...
