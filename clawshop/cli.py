"""End-to-end demo CLI.

Run:
    LLM_MODE=stub python -m clawshop demo

Walks the Maya scenario from PRD §6.1 / user-story A1:
    "we're out of diapers and coffee" → cross-retailer compare → approval →
    checkout, then a watcher tick on a coffee price drop.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from clawshop.agent.orchestrator import Orchestrator
from clawshop.approval.service import ApprovalService, StdinChannel
from clawshop.memory import shelf
from clawshop.memory.store import MemoryStore
from clawshop.memory.write_gate import Candidate, commit_if_allowed
from clawshop.models import Household, Preference, User, WatchedItem
from clawshop.payments.vault import PaymentVault
from clawshop.retailers import (
    AmazonMockAdapter,
    KrogerMockAdapter,
    WalmartMockAdapter,
)
from clawshop.retailers.catalog import CATALOG
from clawshop.watcher.runner import should_ping, tick


def _seed(store: MemoryStore) -> tuple[Household, User]:
    hh = Household(name="Okonkwo")
    user = User(
        household_id=hh.id,
        name="Maya",
        phone="+15551234567",
        auto_approve_limit=20.0,
        trusted_retailers={"walmart", "kroger"},
    )

    store.upsert_preference(
        Preference(
            household_id=hh.id,
            user_id=user.id,
            key="diapers_brand",
            value="Pampers",
            type="brand",
            confidence=0.95,
            source_turn_id="seed",
            ttl_days=180,
        )
    )
    store.upsert_preference(
        Preference(
            household_id=hh.id,
            user_id=user.id,
            key="coffee_brand",
            value="Peet's",
            type="brand",
            confidence=0.95,
            source_turn_id="seed",
            ttl_days=180,
        )
    )

    # Allergy via the gate — exercises the always-confirm path (§11.3).
    res = commit_if_allowed(
        store,
        Candidate(
            household_id=hh.id,
            user_id=user.id,
            key="allergy",
            value="oat milk",
            type="allergy",
            utterance="I'm allergic to oat milk.",
            source_turn_id="seed-allergy",
            prior_session_count=0,
        ),
    )
    # Simulate user confirming the allergy via The Shelf (PRD §11.3 always-confirm).
    if res.verdict == "needs_user_confirm" and res.preference is not None:
        store.upsert_preference(res.preference.model_copy(update={"provisional": False}))
    return hh, user


def _adapters() -> dict:
    return {
        "walmart": WalmartMockAdapter(),
        "kroger": KrogerMockAdapter(),
        "amazon": AmazonMockAdapter(),
    }


def _print_proposal(proposal) -> None:
    print("\n=== Cart proposal ===")
    print(f"  total: ${proposal.total:.2f}")
    for retailer, items in proposal.items_by_retailer.items():
        marker = "(handoff)" if retailer in proposal.handoff_retailers else ""
        print(f"  {retailer} {marker}: ${proposal.total_for(retailer):.2f}")
        for li in items:
            print(f"    - {li.qty}× {li.product.title} @ ${li.product.price:.2f}  — {li.rationale}")


def _print_shelf(store, hh) -> None:
    print("\n=== The Shelf ===")
    for p in shelf.inspect(store, hh.id):
        flags = []
        if p.provisional:
            flags.append("provisional")
        if p.frozen:
            flags.append("frozen")
        if p.ttl_days is None:
            flags.append("never-decays")
        flag_str = f"  [{', '.join(flags)}]" if flags else ""
        print(f"  {p.type:>10}  {p.key:<20} = {p.value!r:<30} conf={p.confidence:.2f}{flag_str}")


async def run_demo() -> int:
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s: %(message)s")

    store = MemoryStore()
    hh, user = _seed(store)
    _print_shelf(store, hh)

    adapters = _adapters()
    vault = PaymentVault()
    channel = StdinChannel()
    approval = ApprovalService(channel, seen_addresses={user.id + "@home"})
    orch = Orchestrator(store=store, adapters=adapters, approval=approval, vault=vault)

    print("\n=== Maya: 'we're out of diapers and coffee' ===")
    result = await orch.run_request(user, "we're out of diapers and coffee")
    _print_proposal(result["proposal"])
    print("\n=== Approvals ===")
    for retailer, req in result["approvals"].items():
        print(f"  {retailer}: {req.decision}  (hits: {req.policy_hits or '—'})")
    print("\n=== Placed orders ===")
    for o in result["placed_orders"]:
        print(f"  {o.retailer}: order={o.id[:8]} total=${o.total:.2f} status={o.status}")
    if result["handoffs"]:
        print("\n=== Hand-off links (Tier D) ===")
        for retailer, link in result["handoffs"].items():
            print(f"  {retailer}: {link}")

    # Watcher demo — coffee drops at Kroger from 14.99 to 12.49.
    print("\n=== Watcher tick: coffee at Kroger ===")
    coffee_kroger = CATALOG["coffee"][1]  # Kroger Peet's
    watch = WatchedItem(
        household_id=hh.id,
        user_id=user.id,
        sku=coffee_kroger.sku,
        retailer="kroger",
        predicate="drop_pct >= 15",
        cooldown_s=3600,
        last_seen_price=14.99,  # before the drop
        perishable=True,
    )
    res = tick([watch], {coffee_kroger.sku: coffee_kroger}, now=datetime.now(timezone.utc))
    print(f"  fired={len(res.fired)}  skipped={res.skipped}")
    for fire in res.fired:
        print(f"  → {fire.product.title}  drop={fire.drop_pct:.1f}%  @ ${fire.product.price:.2f}")
        if should_ping(fire):
            print("    Haiku gate: ping → would deliver perishable approval (5-min timeout)")
        else:
            print("    Haiku gate: skip")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="clawshop")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="run end-to-end demo")
    args = parser.parse_args()
    if args.cmd == "demo":
        raise SystemExit(asyncio.run(run_demo()))


if __name__ == "__main__":
    main()
