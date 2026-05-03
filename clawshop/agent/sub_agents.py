"""Sub-agents: search, compare, checkout. PRD §9.3."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from clawshop.memory.retrieval import RetrievalPack
from clawshop.models import Capabilities, CartProposal, LineItem, Product
from clawshop.retailers.base import RetailerAdapter
from clawshop.retailers.errors import RetailerError

log = logging.getLogger("clawshop.agent")


@dataclass
class SearchHit:
    query_term: str
    product: Product
    rationale: str


def _term_matches_pref(term: str, pref_value: object) -> bool:
    return str(pref_value).lower() in term.lower() or term.lower() in str(pref_value).lower()


async def search_agent(
    adapters: list[RetailerAdapter],
    query_terms: list[str],
    pack: RetrievalPack,
) -> dict[str, list[SearchHit]]:
    """Per-term cross-retailer search. Returns {term: [hits across retailers]}."""
    results: dict[str, list[SearchHit]] = {term: [] for term in query_terms}

    async def _one(adapter: RetailerAdapter, term: str) -> tuple[str, str, list[Product]]:
        try:
            products = await adapter.search(term)
        except RetailerError as e:
            log.warning("search %s/%s failed: %s", adapter.name, term, e)
            products = []
        return adapter.name, term, products

    tasks = [
        _one(a, term)
        for a in adapters
        if Capabilities.SEARCH in a.capabilities()
        for term in query_terms
    ]
    raw = await asyncio.gather(*tasks)
    pref_brand_values = {p.value for p in pack.all_preferences() if p.type == "brand"}
    for retailer, term, products in raw:
        for p in products:
            rationale_bits = [f"matched '{term}'"]
            if p.brand and p.brand in pref_brand_values:
                rationale_bits.append(f"brand '{p.brand}' in your prefs")
            results[term].append(
                SearchHit(query_term=term, product=p, rationale="; ".join(rationale_bits))
            )
    return results


def compare_agent(
    hits_by_term: dict[str, list[SearchHit]],
    pack: RetrievalPack,
    *,
    household_id: str,
) -> CartProposal:
    """Pick the lowest delivered cost per term, preferring brand-matched items."""
    pref_brand_values = {str(p.value).lower() for p in pack.all_preferences() if p.type == "brand"}
    items_by_retailer: dict[str, list[LineItem]] = {}
    handoff = set()

    for term, hits in hits_by_term.items():
        if not hits:
            continue

        def score(h: SearchHit) -> tuple[float, float]:
            # Lower price wins; brand match wins ties (lower secondary key).
            brand_match = 0 if h.product.brand and h.product.brand.lower() in pref_brand_values else 1
            return (h.product.price, brand_match)

        best = min(hits, key=score)
        rationale = best.rationale
        if best.product.brand and best.product.brand.lower() in pref_brand_values:
            rationale = f"{rationale}; preferred brand"
        line = LineItem(product=best.product, qty=1, rationale=rationale)
        items_by_retailer.setdefault(best.product.retailer, []).append(line)
        if best.product.retailer == "amazon":
            handoff.add("amazon")

    return CartProposal(
        household_id=household_id,
        items_by_retailer=items_by_retailer,
        handoff_retailers=handoff,
    )


@dataclass
class CheckoutResult:
    placed_orders: list
    handoff_links: dict[str, str]  # retailer -> deep_link


async def checkout_agent(
    adapters: dict[str, RetailerAdapter],
    proposal: CartProposal,
    *,
    payment_token: str,
    user_id: str,
    household_id: str,
) -> CheckoutResult:
    """Build per-retailer carts; checkout where capability allows, else hand off."""
    placed = []
    handoff = {}
    for retailer, items in proposal.items_by_retailer.items():
        adapter = adapters[retailer]
        cart = await adapter.build_cart(items)
        cart = await adapter.price_cart(cart)
        if Capabilities.CHECKOUT in adapter.capabilities():
            order = await adapter.checkout(
                cart,
                payment_token=payment_token,
                user_id=user_id,
                household_id=household_id,
            )
            placed.append(order)
        else:
            # Tier D: hand off to user (PRD D2).
            handoff[retailer] = cart.deep_link or ""
    return CheckoutResult(placed_orders=placed, handoff_links=handoff)
