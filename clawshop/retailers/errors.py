"""Standardized retailer error taxonomy. PRD §7.4."""

from __future__ import annotations


class RetailerError(Exception):
    code: str = "UNKNOWN"

    def __init__(self, message: str = "", *, retailer: str | None = None) -> None:
        self.retailer = retailer
        super().__init__(f"[{self.code} @ {retailer or '?'}] {message}")


class AuthError(RetailerError):
    code = "AUTH"


class RateLimitError(RetailerError):
    code = "RATE_LIMIT"


class OutOfStockError(RetailerError):
    code = "OUT_OF_STOCK"


class PriceChangedError(RetailerError):
    code = "PRICE_CHANGED"


class TosBlockedError(RetailerError):
    code = "TOS_BLOCKED"


class CaptchaError(RetailerError):
    code = "CAPTCHA"


class UpstreamError(RetailerError):
    code = "UPSTREAM_5XX"


class UnsupportedError(RetailerError):
    code = "UNSUPPORTED"


class UserActionRequiredError(RetailerError):
    code = "USER_ACTION_REQUIRED"
