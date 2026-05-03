"""PaymentVault stub.

The agent fleet only ever sees opaque `paymentToken` strings. The vault is the
only component that can resolve a token to card detail; in this prototype the
"card detail" is a synthetic last-4 generated from the token, never any real PAN.

Hard cap = approved amount + 7% slack (PRD §7.5 / §14.1). Cards auto-close on
first settle or after `lifetime`.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from clawshop.config import SETTINGS
from clawshop.models import PaymentToken


@dataclass
class _CardRecord:
    token: PaymentToken
    last4: str  # synthetic; for display only


class PaymentVault:
    def __init__(self, lifetime: timedelta = timedelta(days=14)) -> None:
        self._records: dict[str, _CardRecord] = {}
        self._lifetime = lifetime

    def issue(self, *, user_id: str, merchant: str, approved_amount: float) -> PaymentToken:
        cap = round(approved_amount * (1.0 + SETTINGS.thresholds.virtual_card_slack_pct), 2)
        token = PaymentToken(
            user_id=user_id,
            merchant=merchant,
            cap=cap,
            expires_at=datetime.now(timezone.utc) + self._lifetime,
        )
        self._records[token.token] = _CardRecord(
            token=token,
            last4=f"{secrets.randbelow(10000):04d}",
        )
        return token

    def settle(self, token: str, amount: float) -> None:
        rec = self._records.get(token)
        if rec is None:
            raise KeyError("unknown token")
        if rec.token.closed:
            raise RuntimeError("card already closed")
        if amount > rec.token.cap:
            raise RuntimeError(f"settlement ${amount:.2f} exceeds cap ${rec.token.cap:.2f}")
        rec.token.closed = True  # PRD §7.5: close on first settle.

    def display_last4(self, token: str) -> str:
        rec = self._records.get(token)
        if rec is None:
            raise KeyError("unknown token")
        return rec.last4

    def is_closed(self, token: str) -> bool:
        rec = self._records.get(token)
        return rec is None or rec.token.closed
