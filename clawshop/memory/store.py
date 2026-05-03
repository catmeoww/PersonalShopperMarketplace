"""SQLite-backed memory store. Append-only audit; hard-delete disabled (PRD §11.2 gate 4)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from clawshop.models import MemoryItem, Preference, SemanticClaim


SCHEMA = """
CREATE TABLE IF NOT EXISTS preferences (
    id TEXT PRIMARY KEY,
    household_id TEXT NOT NULL,
    user_id TEXT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT NOT NULL,
    confidence REAL NOT NULL,
    source_turn_id TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    ttl_days INTEGER,
    provisional INTEGER NOT NULL,
    frozen INTEGER NOT NULL,
    version INTEGER NOT NULL,
    superseded_by TEXT
);
CREATE INDEX IF NOT EXISTS ix_pref_key ON preferences(household_id, user_id, key, version);

CREATE TABLE IF NOT EXISTS episodic (
    id TEXT PRIMARY KEY,
    household_id TEXT NOT NULL,
    user_id TEXT,
    ts TEXT NOT NULL,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL,
    retailer TEXT,
    order_id TEXT,
    source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_epi_hh ON episodic(household_id, ts);

CREATE TABLE IF NOT EXISTS semantic (
    id TEXT PRIMARY KEY,
    household_id TEXT NOT NULL,
    user_id TEXT,
    claim TEXT NOT NULL,
    support_count INTEGER NOT NULL,
    last_seen TEXT NOT NULL,
    confidence REAL NOT NULL,
    provenance TEXT NOT NULL
);
"""


class MemoryStore:
    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    # --- preferences ---------------------------------------------------------

    def upsert_preference(self, pref: Preference) -> Preference:
        """Versioned write. Old row stays (audit). New row gets version+1."""
        cur = self.conn.execute(
            "SELECT MAX(version) AS v FROM preferences "
            "WHERE household_id=? AND COALESCE(user_id,'') = COALESCE(?, '') AND key=?",
            (pref.household_id, pref.user_id, pref.key),
        )
        row = cur.fetchone()
        next_version = (row["v"] or 0) + 1
        if next_version > 1:
            # mark previous as superseded
            self.conn.execute(
                "UPDATE preferences SET superseded_by=? WHERE household_id=? "
                "AND COALESCE(user_id,'')=COALESCE(?, '') AND key=? AND version=?",
                (pref.id, pref.household_id, pref.user_id, pref.key, next_version - 1),
            )
        new = pref.model_copy(update={"version": next_version})
        self.conn.execute(
            "INSERT INTO preferences VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)",
            (
                new.id,
                new.household_id,
                new.user_id,
                new.key,
                json.dumps(new.value),
                new.type,
                new.confidence,
                new.source_turn_id,
                new.source,
                new.created_at.isoformat(),
                new.updated_at.isoformat(),
                new.ttl_days,
                int(new.provisional),
                int(new.frozen),
                new.version,
            ),
        )
        self.conn.commit()
        return new

    def get_preference(
        self, household_id: str, user_id: str | None, key: str
    ) -> Preference | None:
        cur = self.conn.execute(
            "SELECT * FROM preferences WHERE household_id=? "
            "AND COALESCE(user_id,'')=COALESCE(?, '') AND key=? "
            "AND superseded_by IS NULL ORDER BY version DESC LIMIT 1",
            (household_id, user_id, key),
        )
        row = cur.fetchone()
        return _row_to_pref(row) if row else None

    def list_preferences(self, household_id: str) -> list[Preference]:
        cur = self.conn.execute(
            "SELECT * FROM preferences WHERE household_id=? AND superseded_by IS NULL "
            "ORDER BY type, key",
            (household_id,),
        )
        return [_row_to_pref(r) for r in cur.fetchall()]

    # --- episodic ------------------------------------------------------------

    def append_episodic(self, item: MemoryItem) -> MemoryItem:
        self.conn.execute(
            "INSERT INTO episodic VALUES (?,?,?,?,?,?,?,?,?)",
            (
                item.id,
                item.household_id,
                item.user_id,
                item.ts.isoformat(),
                item.kind,
                json.dumps(item.payload),
                item.retailer,
                item.order_id,
                item.source,
            ),
        )
        self.conn.commit()
        return item

    def list_episodic(
        self, household_id: str, kinds: Iterable[str] | None = None
    ) -> list[MemoryItem]:
        sql = "SELECT * FROM episodic WHERE household_id=?"
        params: list[Any] = [household_id]
        if kinds:
            placeholders = ",".join("?" for _ in kinds)
            sql += f" AND kind IN ({placeholders})"
            params.extend(kinds)
        sql += " ORDER BY ts DESC"
        cur = self.conn.execute(sql, params)
        return [_row_to_episodic(r) for r in cur.fetchall()]

    # --- semantic ------------------------------------------------------------

    def upsert_semantic(self, claim: SemanticClaim) -> SemanticClaim:
        self.conn.execute(
            "INSERT OR REPLACE INTO semantic VALUES (?,?,?,?,?,?,?,?)",
            (
                claim.id,
                claim.household_id,
                claim.user_id,
                claim.claim,
                claim.support_count,
                claim.last_seen.isoformat(),
                claim.confidence,
                json.dumps(claim.provenance),
            ),
        )
        self.conn.commit()
        return claim

    def list_semantic(self, household_id: str) -> list[SemanticClaim]:
        cur = self.conn.execute(
            "SELECT * FROM semantic WHERE household_id=? ORDER BY confidence DESC",
            (household_id,),
        )
        return [_row_to_semantic(r) for r in cur.fetchall()]


def _row_to_pref(row: sqlite3.Row) -> Preference:
    return Preference(
        id=row["id"],
        household_id=row["household_id"],
        user_id=row["user_id"],
        key=row["key"],
        value=json.loads(row["value"]),
        type=row["type"],
        confidence=row["confidence"],
        source_turn_id=row["source_turn_id"],
        source=row["source"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        ttl_days=row["ttl_days"],
        provisional=bool(row["provisional"]),
        frozen=bool(row["frozen"]),
        version=row["version"],
    )


def _row_to_episodic(row: sqlite3.Row) -> MemoryItem:
    return MemoryItem(
        id=row["id"],
        household_id=row["household_id"],
        user_id=row["user_id"],
        ts=datetime.fromisoformat(row["ts"]),
        kind=row["kind"],
        payload=json.loads(row["payload"]),
        retailer=row["retailer"],
        order_id=row["order_id"],
        source=row["source"],
    )


def _row_to_semantic(row: sqlite3.Row) -> SemanticClaim:
    return SemanticClaim(
        id=row["id"],
        household_id=row["household_id"],
        user_id=row["user_id"],
        claim=row["claim"],
        support_count=row["support_count"],
        last_seen=datetime.fromisoformat(row["last_seen"]),
        confidence=row["confidence"],
        provenance=json.loads(row["provenance"]),
    )
