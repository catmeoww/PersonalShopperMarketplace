"""Config: model routing per PRD §9.4, thresholds per §11.3 / §12, env loader."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

# Model IDs per environment knowledge cutoff.
HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-7"

Step = Literal[
    "intent",
    "watcher_gate",
    "memory_extract",
    "memory_classify",
    "memory_dedup",
    "plan_chat",
    "tool_args",
    "ambiguous",
    "reflection",
]

# PRD §9.4.
MODEL_ROUTING: dict[str, str] = {
    "intent": HAIKU,
    "watcher_gate": HAIKU,
    "memory_extract": HAIKU,
    "memory_classify": HAIKU,
    "memory_dedup": SONNET,
    "plan_chat": SONNET,
    "tool_args": SONNET,
    "ambiguous": OPUS,
    "reflection": HAIKU,
}


@dataclass(frozen=True)
class Thresholds:
    # PRD §11.3
    auto_commit_confidence: float = 0.85
    provisional_floor: float = 0.6
    # PRD §12.4
    default_approval_timeout_s: int = 30 * 60
    perishable_approval_timeout_s: int = 5 * 60
    # PRD §7.5
    virtual_card_slack_pct: float = 0.07
    # PRD §12.1
    new_address_window_days: int = 30
    quiet_hours_start: int = 2
    quiet_hours_end: int = 6
    delta_from_estimate_pct: float = 0.15


# PRD §11.4 — TTL by type (days; None = never decays).
TTL_DAYS: dict[str, int | None] = {
    "brand": 180,
    "size": 180,
    "schedule": 90,
    "cadence": 90,
    "budget": 365,
    "allergy": None,
    "medical": None,
    "dietary": 365,
}

# PRD §11.3 — keys that always need user confirmation regardless of confidence.
ALWAYS_CONFIRM_KEYS: frozenset[str] = frozenset({"allergy", "medical"})

# PRD §11.5 — only these source tags can write to preferences/semantic.
TRUSTED_SOURCES: frozenset[str] = frozenset(
    {"user_turn", "confirmed_order", "user_approved_tool_output"}
)

# PRD §12.1 — categories that always escalate individually.
SENSITIVE_CATEGORIES: frozenset[str] = frozenset(
    {"alcohol", "pharmacy", "firearms", "gift_card"}
)


@dataclass(frozen=True)
class Settings:
    llm_mode: str = field(default_factory=lambda: os.environ.get("LLM_MODE", "stub"))
    api_key: str | None = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY")
    )
    thresholds: Thresholds = field(default_factory=Thresholds)


SETTINGS = Settings()
