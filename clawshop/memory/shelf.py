"""The Shelf — user-facing memory inspect / edit / freeze / export. PRD §7.2, B3."""

from __future__ import annotations

import json

from clawshop.memory.store import MemoryStore
from clawshop.models import Preference


def inspect(store: MemoryStore, household_id: str) -> list[Preference]:
    return store.list_preferences(household_id)


def freeze(store: MemoryStore, pref: Preference) -> Preference:
    return store.upsert_preference(pref.model_copy(update={"frozen": True}))


def unfreeze(store: MemoryStore, pref: Preference) -> Preference:
    return store.upsert_preference(pref.model_copy(update={"frozen": False}))


def edit(store: MemoryStore, pref: Preference, new_value: object) -> Preference:
    if pref.frozen:
        raise ValueError("preference is frozen; unfreeze first")
    return store.upsert_preference(pref.model_copy(update={"value": new_value}))


def export_json(store: MemoryStore, household_id: str) -> str:
    """JSON export for CCPA/CPRA + GDPR. PRD §14.3."""
    payload = {
        "preferences": [p.model_dump(mode="json") for p in store.list_preferences(household_id)],
        "episodic": [e.model_dump(mode="json") for e in store.list_episodic(household_id)],
        "semantic": [s.model_dump(mode="json") for s in store.list_semantic(household_id)],
    }
    return json.dumps(payload, indent=2, default=str)
