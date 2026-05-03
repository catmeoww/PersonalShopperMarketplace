"""In-memory product fixtures across retailers, used by the mock adapters.

Designed so the same logical item (e.g. diapers, coffee) exists at multiple
retailers with different prices — exercising cross-retailer compare (PRD §6.1, A1).
"""

from __future__ import annotations

from clawshop.models import Product

# Each entry: list of Products (one per retailer).
# Keyed loosely so the search step can fuzzy-match natural language.
CATALOG: dict[str, list[Product]] = {
    "diapers": [
        Product(
            sku="WMT-DIAP-PMP-S5",
            retailer="walmart",
            title="Pampers Swaddlers Size 5 (148 ct)",
            brand="Pampers",
            size="size 5",
            price=43.97,
            category="grocery",
        ),
        Product(
            sku="KRO-DIAP-PMP-S5",
            retailer="kroger",
            title="Pampers Swaddlers Size 5 (148 ct)",
            brand="Pampers",
            size="size 5",
            price=44.99,
            category="grocery",
        ),
        Product(
            sku="AMZ-DIAP-PMP-S5",
            retailer="amazon",
            title="Pampers Swaddlers Size 5 (148 ct)",
            brand="Pampers",
            size="size 5",
            price=42.50,
            category="grocery",
        ),
    ],
    "coffee": [
        Product(
            sku="WMT-CFE-PEET",
            retailer="walmart",
            title="Peet's Major Dickason's Whole Bean 18oz",
            brand="Peet's",
            size="18 oz",
            price=14.99,
            category="grocery",
        ),
        Product(
            sku="KRO-CFE-PEET",
            retailer="kroger",
            title="Peet's Major Dickason's Whole Bean 18oz",
            brand="Peet's",
            size="18 oz",
            price=12.49,
            deal_tags=["price_drop"],
            category="grocery",
        ),
        Product(
            sku="AMZ-CFE-PEET",
            retailer="amazon",
            title="Peet's Major Dickason's Whole Bean 18oz",
            brand="Peet's",
            size="18 oz",
            price=13.99,
            category="grocery",
        ),
    ],
    "milk": [
        Product(
            sku="KRO-MLK-WHOLE-1G",
            retailer="kroger",
            title="Horizon Organic Whole Milk 1gal",
            brand="Horizon Organic",
            size="1 gal",
            price=5.49,
            category="grocery",
        ),
    ],
    "oat_milk": [
        Product(
            sku="WMT-OAT-OATLY",
            retailer="walmart",
            title="Oatly Original Oat Milk 64oz",
            brand="Oatly",
            size="64 oz",
            price=4.99,
            category="grocery",
        ),
    ],
    "wine": [  # used to exercise sensitive-category branch
        Product(
            sku="WMT-WIN-RED",
            retailer="walmart",
            title="Bota Box Cabernet 3L",
            brand="Bota Box",
            size="3 L",
            price=18.99,
            category="alcohol",
        ),
    ],
}


def search(query: str, retailer: str, *, limit: int = 5) -> list[Product]:
    """Fuzzy keyword match across CATALOG. Restricted to one retailer."""
    q = query.lower()
    matches: list[Product] = []
    for key, products in CATALOG.items():
        key_match = any(tok in q for tok in key.replace("_", " ").split())
        for p in products:
            if p.retailer != retailer:
                continue
            text = (p.title + " " + (p.brand or "") + " " + key).lower()
            if key_match or any(tok in text for tok in q.split()):
                matches.append(p)
    return matches[:limit]


def get(sku: str) -> Product | None:
    for products in CATALOG.values():
        for p in products:
            if p.sku == sku:
                return p
    return None
