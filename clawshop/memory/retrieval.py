"""Hybrid retrieval with hard-pins. PRD §11.6.

Token budget split (40/30/20/10) is enforced as item-count budgets in the prototype.
Allergy / medical / active-order pins are never evicted.
"""

from __future__ import annotations

from dataclasses import dataclass

from clawshop.config import ALWAYS_CONFIRM_KEYS
from clawshop.memory.store import MemoryStore
from clawshop.models import MemoryItem, Preference, SemanticClaim


@dataclass
class RetrievalPack:
    preferences: list[Preference]
    semantic: list[SemanticClaim]
    episodic: list[MemoryItem]
    pinned: list[Preference]  # subset of preferences guaranteed present

    def all_preferences(self) -> list[Preference]:
        seen = {p.id for p in self.pinned}
        return self.pinned + [p for p in self.preferences if p.id not in seen]


def retrieve(
    store: MemoryStore,
    household_id: str,
    *,
    item_budget: int = 20,
    query_terms: list[str] | None = None,
) -> RetrievalPack:
    """Retrieve memory for an agent turn.

    Hard-pins (allergy + medical + active orders) are added FIRST and cannot be
    evicted. The remaining budget is split 40/30/20 across remaining
    preferences / semantic / episodic.
    """
    query_terms = [t.lower() for t in (query_terms or [])]

    all_prefs = store.list_preferences(household_id)
    pinned = [p for p in all_prefs if p.type in ALWAYS_CONFIRM_KEYS]
    rest_prefs = [p for p in all_prefs if p not in pinned]

    # Active orders are episodic items with kind='order' and status not settled.
    active_orders = [
        e
        for e in store.list_episodic(household_id, kinds=("order",))
        if e.payload.get("status") in (None, "placed", "handoff")
    ]

    # Score remaining prefs by query overlap.
    def pref_score(p: Preference) -> float:
        s = p.confidence
        text = f"{p.key} {p.value}".lower()
        s += sum(0.5 for t in query_terms if t in text)
        return s

    rest_prefs.sort(key=pref_score, reverse=True)

    remaining = max(0, item_budget - len(pinned) - len(active_orders))
    pref_budget = max(1, int(remaining * 0.40))
    sem_budget = max(1, int(remaining * 0.30))
    epi_budget = max(0, remaining - pref_budget - sem_budget)

    semantic = store.list_semantic(household_id)[:sem_budget]
    episodic = active_orders + store.list_episodic(household_id)[: max(0, epi_budget)]

    return RetrievalPack(
        preferences=rest_prefs[:pref_budget],
        semantic=semantic,
        episodic=episodic,
        pinned=pinned,
    )
