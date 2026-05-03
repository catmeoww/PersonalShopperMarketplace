"""Amazon Tier D adapter. PRD §13.2 / D2 — search + cart-link handoff only.

`checkout` raises UnsupportedError so the orchestrator routes Amazon line items
to a handoff cart instead of attempting programmatic checkout.
"""

from __future__ import annotations

from clawshop.models import Cart, Capabilities, LineItem, Order, Product
from clawshop.retailers import catalog
from clawshop.retailers.base import RetailerAdapter
from clawshop.retailers.errors import OutOfStockError, UnsupportedError


class AmazonMockAdapter(RetailerAdapter):
    name = "amazon"

    def capabilities(self) -> Capabilities:
        # Tier D: search and a handoff link, nothing programmatic.
        return Capabilities.SEARCH | Capabilities.GET_PRODUCT | Capabilities.BUILD_CART

    async def search(self, query: str, *, limit: int = 5) -> list[Product]:
        return catalog.search(query, self.name, limit=limit)

    async def get_product(self, sku: str) -> Product:
        p = catalog.get(sku)
        if p is None or p.retailer != self.name:
            raise OutOfStockError(f"sku {sku} not in catalog", retailer=self.name)
        return p

    async def build_cart(self, items: list[LineItem]) -> Cart:
        total = sum(li.product.price * li.qty for li in items)
        # PA-API doesn't support real cart construction; we synthesize a
        # smile.amazon.com/gp/aws/cart/add.html-style URL for a manual finish.
        params = "&".join(
            f"ASIN.{i + 1}={li.product.sku}&Quantity.{i + 1}={li.qty}"
            for i, li in enumerate(items)
        )
        return Cart(
            retailer=self.name,
            items=items,
            deep_link=f"https://amazon.example/gp/aws/cart/add.html?{params}",
            total=total,
        )

    async def price_cart(self, cart: Cart) -> Cart:
        return cart

    async def checkout(
        self, cart: Cart, *, payment_token: str, user_id: str, household_id: str
    ) -> Order:
        # Tier D: no programmatic checkout; orchestrator must surface handoff.
        raise UnsupportedError(
            "Amazon is Tier D (handoff only). Use the cart deep_link.",
            retailer=self.name,
        )

    async def get_order(self, order_id: str) -> Order:
        raise UnsupportedError("Amazon order lookup not in MVP.", retailer=self.name)

    async def cancel(self, order_id: str) -> bool:
        raise UnsupportedError("Amazon cancel not in MVP.", retailer=self.name)
