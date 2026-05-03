"""Retailer adapter layer. PRD §7.4 / §13."""

from clawshop.retailers.amazon_mock import AmazonMockAdapter
from clawshop.retailers.base import RetailerAdapter
from clawshop.retailers.errors import (
    RetailerError,
    AuthError,
    RateLimitError,
    OutOfStockError,
    PriceChangedError,
    TosBlockedError,
    CaptchaError,
    UpstreamError,
    UnsupportedError,
    UserActionRequiredError,
)
from clawshop.retailers.kroger_mock import KrogerMockAdapter
from clawshop.retailers.walmart_mock import WalmartMockAdapter

__all__ = [
    "RetailerAdapter",
    "WalmartMockAdapter",
    "KrogerMockAdapter",
    "AmazonMockAdapter",
    "RetailerError",
    "AuthError",
    "RateLimitError",
    "OutOfStockError",
    "PriceChangedError",
    "TosBlockedError",
    "CaptchaError",
    "UpstreamError",
    "UnsupportedError",
    "UserActionRequiredError",
]
