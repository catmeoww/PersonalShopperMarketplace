"""Retrieval correctness — allergy hard-pin must always be present (PRD §11.6)."""

from __future__ import annotations

from clawshop.memory.retrieval import retrieve
from clawshop.memory.store import MemoryStore
from clawshop.models import Preference


def test_allergy_pinned_even_with_tiny_budget():
    store = MemoryStore()
    hh = "hh-1"
    # Many low-priority brand prefs.
    for i in range(20):
        store.upsert_preference(
            Preference(
                household_id=hh,
                user_id="u",
                key=f"brand_{i}",
                value=f"BrandX{i}",
                type="brand",
                confidence=0.5,
                source_turn_id=f"t{i}",
            )
        )
    # Allergy.
    store.upsert_preference(
        Preference(
            household_id=hh,
            user_id="u",
            key="allergy",
            value="peanuts",
            type="allergy",
            confidence=1.0,
            source_turn_id="t-allergy",
            ttl_days=None,
        )
    )

    pack = retrieve(store, hh, item_budget=2)
    pinned_keys = {p.key for p in pack.pinned}
    assert "allergy" in pinned_keys
    # Allergy must be retrieved even if budget is exhausted.
    all_returned = {p.key for p in pack.all_preferences()}
    assert "allergy" in all_returned


def test_query_terms_boost_relevance():
    store = MemoryStore()
    hh = "hh-1"
    store.upsert_preference(
        Preference(
            household_id=hh,
            user_id="u",
            key="diapers_brand",
            value="Pampers",
            type="brand",
            confidence=0.8,
            source_turn_id="t1",
        )
    )
    store.upsert_preference(
        Preference(
            household_id=hh,
            user_id="u",
            key="coffee_brand",
            value="Peet's",
            type="brand",
            confidence=0.8,
            source_turn_id="t2",
        )
    )
    pack = retrieve(store, hh, item_budget=4, query_terms=["diapers"])
    keys = [p.key for p in pack.preferences]
    assert keys[0] == "diapers_brand"
