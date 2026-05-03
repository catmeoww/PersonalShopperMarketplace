"""Memory write-gate. PRD §11.2 (four checks) + §11.3 (commit thresholds) + §11.5 (poisoning)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from clawshop import llm
from clawshop.config import (
    ALWAYS_CONFIRM_KEYS,
    SETTINGS,
    TRUSTED_SOURCES,
    TTL_DAYS,
)
from clawshop.memory.store import MemoryStore
from clawshop.models import Preference, PrefType

Verdict = Literal["commit", "provisional", "drop", "needs_user_confirm"]


@dataclass
class Candidate:
    household_id: str
    user_id: str | None
    key: str
    value: object
    type: PrefType
    utterance: str  # the supporting raw text (verbatim)
    source_turn_id: str
    source: str = "user_turn"
    prior_session_count: int = 0  # count of distinct sessions where this pref was observed


@dataclass
class GateResult:
    verdict: Verdict
    confidence: float
    reasons: list[str]
    preference: Preference | None = None  # populated on commit/provisional


_IMPERATIVE_CUES = ("always", "never", "i'm allergic", "i am allergic", "we always", "we never")


def _has_imperative(utterance: str) -> bool:
    u = utterance.lower()
    return any(c in u for c in _IMPERATIVE_CUES)


def _evidence_passes(c: Candidate) -> bool:
    """Gate 1: ≥2 distinct sessions OR imperative language."""
    return c.prior_session_count >= 1 or _has_imperative(c.utterance)


def _classify(c: Candidate) -> str:
    """Gate 2: Haiku-tier classifier — preference | one-off | noise."""
    return llm.complete(
        "memory_classify",
        system="Classify a candidate user preference. "
        "Return one of: preference, one-off, noise. "
        "Single-mention sarcasm or jokes are noise.",
        user=f"key={c.key} value={c.value!r} utterance={c.utterance!r}",
    ).strip().lower()


def _conflict_check(store: MemoryStore, c: Candidate) -> Preference | None:
    return store.get_preference(c.household_id, c.user_id, c.key)


def _confidence(c: Candidate, classifier: str) -> float:
    """Heuristic — bumped by imperative cues and prior support."""
    base = 0.5
    if _has_imperative(c.utterance):
        base += 0.35
    if c.prior_session_count >= 1:
        base += 0.15
    if classifier == "preference":
        base += 0.05
    return min(base, 1.0)


def evaluate(store: MemoryStore, c: Candidate) -> GateResult:
    reasons: list[str] = []

    # PRD §11.5 — source-trust filter. Untrusted sources go to episodic only.
    if c.source not in TRUSTED_SOURCES:
        return GateResult(
            verdict="drop",
            confidence=0.0,
            reasons=["source_untrusted"],
        )

    # Gate 1: evidence threshold.
    if not _evidence_passes(c):
        return GateResult(verdict="drop", confidence=0.3, reasons=["insufficient_evidence"])
    reasons.append("evidence_ok")

    # Gate 2: classifier pass.
    classifier = _classify(c)
    if classifier != "preference":
        return GateResult(
            verdict="drop",
            confidence=0.2,
            reasons=[f"classifier={classifier}"],
        )
    reasons.append("classifier=preference")

    # Allergy / medical short-circuit (PRD §11.3) — always user-confirm.
    if c.type in ALWAYS_CONFIRM_KEYS or c.key in ALWAYS_CONFIRM_KEYS:
        pref = _build_pref(c, confidence=1.0, provisional=True)
        return GateResult(
            verdict="needs_user_confirm",
            confidence=1.0,
            reasons=reasons + ["medical_or_allergy"],
            preference=pref,
        )

    # Gate 3: conflict check. If contradicts, route to user-confirm.
    existing = _conflict_check(store, c)
    if existing and existing.value != c.value and not existing.frozen:
        # Money-affecting params (§11.5): always user-confirm.
        pref = _build_pref(c, confidence=_confidence(c, classifier), provisional=True)
        return GateResult(
            verdict="needs_user_confirm",
            confidence=pref.confidence,
            reasons=reasons + ["conflict_with_existing"],
            preference=pref,
        )

    # Gate 4: provenance is intrinsic — Candidate carries source_turn_id and utterance.
    reasons.append("provenance_ok")

    conf = _confidence(c, classifier)
    if conf >= SETTINGS.thresholds.auto_commit_confidence:
        return GateResult(
            verdict="commit",
            confidence=conf,
            reasons=reasons,
            preference=_build_pref(c, confidence=conf, provisional=False),
        )
    if conf >= SETTINGS.thresholds.provisional_floor:
        return GateResult(
            verdict="provisional",
            confidence=conf,
            reasons=reasons + ["below_auto_commit"],
            preference=_build_pref(c, confidence=conf, provisional=True),
        )
    return GateResult(verdict="drop", confidence=conf, reasons=reasons + ["below_provisional"])


def _build_pref(c: Candidate, confidence: float, provisional: bool) -> Preference:
    return Preference(
        household_id=c.household_id,
        user_id=c.user_id,
        key=c.key,
        value=c.value,
        type=c.type,
        confidence=confidence,
        source_turn_id=c.source_turn_id,
        source=c.source,
        ttl_days=TTL_DAYS.get(c.type, 180),
        provisional=provisional,
    )


def commit_if_allowed(store: MemoryStore, c: Candidate) -> GateResult:
    """Apply gate; persist on commit/provisional. Returns the result either way."""
    res = evaluate(store, c)
    if res.preference and res.verdict in ("commit", "provisional"):
        store.upsert_preference(res.preference)
    return res
