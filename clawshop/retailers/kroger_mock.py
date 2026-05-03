"""Kroger Tier B adapter. PRD §13.1 — public API, cart yes / checkout no."""

from __future__ import annotations

from clawshop.models import Cart, Capabilities, LineItem, Order, Product
from clawshop.retailers import catalog
from clawshop.retailers.base import RetailerAdapter
from clawshop.retailers.errors import OutOfStockError


class KrogerMockAdapter(RetailerAdapter):
    name = "kroger"

    def capabilities(self) -> Capabilities:
        return (
            Capabilities.SEARCH
            | Capabilities.GET_PRODUCT
            | Capabilities.BUILD_CART
            | Capabilities.PRICE_CART
            | Capabilities.CHECKOUT  # mock: simulate Tier B handoff completing as success
            | Capabilities.CANCEL
        )

    async def search(self, query: str, *, limit: int = 5) -> list[Product]:
        return catalog.search(query, self.name, limit=limit)

    async def get_product(self, sku: str) -> Product:
        p = catalog.get(sku)
        if p is None or p.retailer != self.name:
            raise OutOfStockError(f"sku {sku} not in catalog", retailer=self.name)
        return p

    async def build_cart(self, items: list[LineItem]) -> Cart:
        total = sum(li.product.price * li.qty for li in items)
        skus = ",".join(f"{li.product.sku}:{li.qty}" for li in items)
        return Cart(
            retailer=self.name,
            items=items,
            deep_link=f"https://kroger.example/cart?items={skus}",
            total=total,
        )

    async def price_cart(self, cart: Cart) -> Cart:
        return cart

    async def checkout(
        self, cart: Cart, *, payment_token: str, user_id: str, household_id: str
    ) -> Order:
        return Order(
            household_id=household_id,
            user_id=user_id,
            retailer=self.name,
            items=cart.items,
            total=cart.total,
            status="placed",
            payment_token=payment_token,
        )

    async def get_order(self, order_id: str) -> Order:
        raise NotImplementedError("mock")

    async def cancel(self, order_id: str) -> bool:
        return True
