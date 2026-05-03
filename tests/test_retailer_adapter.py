"""Retailer adapter contract conformance + Tier D handoff behavior."""

from __future__ import annotations

import asyncio

import pytest

from clawshop.models import Capabilities, LineItem
from clawshop.retailers import (
    AmazonMockAdapter,
    KrogerMockAdapter,
    UnsupportedError,
    WalmartMockAdapter,
)


@pytest.fixture
def adapters():
    return [WalmartMockAdapter(), KrogerMockAdapter(), AmazonMockAdapter()]


def test_all_adapters_implement_search(adapters):
    for a in adapters:
        results = asyncio.run(a.search("coffee"))
        assert isinstance(results, list)
        for p in results:
            assert p.retailer == a.name


def test_walmart_kroger_can_checkout(adapters):
    walmart, kroger, _ = adapters
    assert Capabilities.CHECKOUT in walmart.capabilities()
    assert Capabilities.CHECKOUT in kroger.capabilities()


def test_amazon_tier_d_no_checkout(adapters):
    """PRD D2 / §13.2: Amazon is search + handoff only."""
    _, _, amazon = adapters
    assert Capabilities.CHECKOUT not in amazon.capabilities()
    products = asyncio.run(amazon.search("coffee"))
    cart = asyncio.run(amazon.build_cart([LineItem(product=products[0], qty=1)]))
    assert "amazon" in cart.deep_link
    with pytest.raises(UnsupportedError):
        asyncio.run(
            amazon.checkout(cart, payment_token="t", user_id="u", household_id="hh")
        )


def test_walmart_build_cart_returns_deep_link(adapters):
    walmart = adapters[0]
    products = asyncio.run(walmart.search("diapers"))
    assert products
    cart = asyncio.run(walmart.build_cart([LineItem(product=products[0], qty=2)]))
    assert cart.deep_link and cart.deep_link.startswith("https://walmart.example/")
    assert cart.total == products[0].price * 2


def test_cross_retailer_finds_diapers(adapters):
    walmart, kroger, amazon = adapters
    w = asyncio.run(walmart.search("diapers"))
    k = asyncio.run(kroger.search("diapers"))
    a = asyncio.run(amazon.search("diapers"))
    assert all(len(r) > 0 for r in (w, k, a))
    # Different retailers, different prices, same brand.
    assert {p.retailer for p in (w + k + a)} == {"walmart", "kroger", "amazon"}
