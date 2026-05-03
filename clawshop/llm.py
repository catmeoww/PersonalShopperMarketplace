"""Anthropic SDK wrapper with model routing per PRD §9.4.

`LLM_MODE=stub` returns deterministic fixtures so tests run without an API key.
The cost-per-turn guardrail (PRD §8) is logged per call.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from clawshop.config import MODEL_ROUTING, SETTINGS, Step

log = logging.getLogger("clawshop.llm")


@dataclass
class CallLog:
    step: str
    model: str
    input_chars: int
    output_chars: int


_calls: list[CallLog] = []


def call_log() -> list[CallLog]:
    return list(_calls)


def reset_log() -> None:
    _calls.clear()


def route(step: Step) -> str:
    return MODEL_ROUTING[step]


def _stub(step: Step, system: str, user: str) -> str:
    """Deterministic offline behavior covering the steps the demo + tests exercise."""
    text = user.lower()

    if step == "intent":
        # Tiny rule-based intent classifier.
        if any(k in text for k in ("price drop", "deal", "back in stock")):
            return "watcher_wake"
        if any(k in text for k in ("out of", "need", "buy", "order")):
            return "chat"
        return "chat"

    if step == "memory_classify":
        # PRD §11.2 gate 2: preference | one-off | noise.
        # Imperative cues OR negation → preference.
        if any(
            cue in text
            for cue in ("always", "never", "i'm allergic", "i am allergic", "we always")
        ):
            return "preference"
        if any(cue in text for cue in ("just kidding", "lol", "haha")):
            return "noise"
        return "one-off"

    if step == "watcher_gate":
        # "Is this worth pinging?" — say yes for material drops, no for noise.
        m = re.search(r"drop_pct=([0-9.]+)", text)
        if m and float(m.group(1)) < 5:
            return "skip"
        return "ping"

    if step == "memory_extract":
        # Return JSON list of candidate atoms.
        return "[]"

    if step == "memory_dedup":
        # No conflict.
        return "no_conflict"

    if step == "plan_chat":
        return "search_then_compare"

    if step == "tool_args":
        return "{}"

    if step == "ambiguous":
        return "ask_user"

    if step == "reflection":
        return "ok"

    return ""


def complete(step: Step, system: str, user: str, **kwargs: Any) -> str:
    model = route(step)
    if SETTINGS.llm_mode == "stub" or not SETTINGS.api_key:
        out = _stub(step, system, user)
        _calls.append(CallLog(step, model + "(stub)", len(system) + len(user), len(out)))
        log.info("llm.stub step=%s model=%s out=%s", step, model, out[:80])
        return out

    # Live path.
    import anthropic  # local import so stub mode doesn't require the dep at import time

    client = anthropic.Anthropic(api_key=SETTINGS.api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=kwargs.get("max_tokens", 512),
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    out = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    _calls.append(CallLog(step, model, len(system) + len(user), len(out)))
    log.info("llm.live step=%s model=%s in=%d out=%d", step, model, len(user), len(out))
    return out


def complete_json(step: Step, system: str, user: str, **kwargs: Any) -> Any:
    raw = complete(step, system, user, **kwargs)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
