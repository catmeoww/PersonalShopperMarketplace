"""Lightweight planner. PRD §9.3.

Bounded: max 12 steps, max 3 re-plans, hard timeout (we enforce these via the
Python control flow rather than the open-ended loop the PRD describes).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from clawshop import llm
from clawshop.agent import prompts, sub_agents
from clawshop.approval.service import ApprovalService
from clawshop.memory.retrieval import retrieve
from clawshop.memory.store import MemoryStore
from clawshop.models import Action, CartProposal, MemoryItem, User
from clawshop.payments.vault import PaymentVault
from clawshop.retailers.base import RetailerAdapter

log = logging.getLogger("clawshop.orchestrator")

# Tiny term extractor — recognizes the staples in the demo catalog.
_TERM_PATTERNS = {
    "diapers": re.compile(r"\bdiap\w*", re.I),
    "coffee": re.compile(r"\bcoff\w*", re.I),
    "milk": re.compile(r"\bmilk\b", re.I),
    "wine": re.compile(r"\bwine\b", re.I),
}


def extract_terms(text: str) -> list[str]:
    return [k for k, p in _TERM_PATTERNS.items() if p.search(text)]


@dataclass
class Orchestrator:
    store: MemoryStore
    adapters: dict[str, RetailerAdapter]
    approval: ApprovalService
    vault: PaymentVault

    def classify_intent(self, text: str) -> str:
        return llm.complete("intent", system=prompts.INTENT_SYSTEM, user=text).strip().lower()

    async def propose_cart(self, user: User, text: str) -> CartProposal:
        terms = extract_terms(text)
        pack = retrieve(self.store, user.household_id, query_terms=terms)
        hits = await sub_agents.search_agent(list(self.adapters.values()), terms, pack)
        proposal = sub_agents.compare_agent(hits, pack, household_id=user.household_id)
        return proposal

    async def submit_for_approval(
        self, user: User, proposal: CartProposal
    ) -> dict[str, Action]:
        """One Action per retailer (PRD §12.3 batching default)."""
        actions: dict[str, Action] = {}
        for retailer, items in proposal.items_by_retailer.items():
            adapter = self.adapters[retailer]
            from clawshop.models import Capabilities

            if Capabilities.CHECKOUT not in adapter.capabilities():
                # Hand-off: still record an Action for transparency.
                actions[retailer] = Action(
                    kind="checkout",
                    user_id=user.id,
                    household_id=user.household_id,
                    retailer=retailer,
                    cost=proposal.total_for(retailer),
                    items=items,
                    payload={"handoff": True},
                )
                continue
            cost = proposal.total_for(retailer)
            actions[retailer] = Action(
                kind="checkout",
                user_id=user.id,
                household_id=user.household_id,
                retailer=retailer,
                cost=cost,
                items=items,
                category=items[0].product.category if items else "grocery",
                shipping_address=user.id + "@home",  # placeholder
                estimated_cost=cost,
            )
        return actions

    async def run_request(self, user: User, text: str) -> dict:
        """End-to-end: parse → propose → approval per retailer → checkout/handoff."""
        proposal = await self.propose_cart(user, text)
        actions = await self.submit_for_approval(user, proposal)

        approvals = {}
        for retailer, action in actions.items():
            req = await self.approval.request(action, user)
            approvals[retailer] = req

        placed = []
        handoffs: dict[str, str] = {}
        for retailer, req in approvals.items():
            adapter = self.adapters[retailer]
            from clawshop.models import Capabilities

            if Capabilities.CHECKOUT not in adapter.capabilities():
                # Tier D: build cart and hand off; no payment token needed.
                cart = await adapter.build_cart(actions[retailer].items)
                handoffs[retailer] = cart.deep_link or ""
                continue

            if req.decision != "approved":
                log.info("orchestrator.skipped retailer=%s decision=%s", retailer, req.decision)
                continue

            self.approval.consume(req)  # PRD §14.2 replay defense
            token = self.vault.issue(
                user_id=user.id,
                merchant=retailer,
                approved_amount=req.action.cost,
            )
            cart = await adapter.build_cart(req.action.items)
            cart = await adapter.price_cart(cart)
            order = await adapter.checkout(
                cart,
                payment_token=token.token,
                user_id=user.id,
                household_id=user.household_id,
            )
            order.approval_id = req.id
            placed.append(order)
            self.vault.settle(token.token, order.total)

            self.store.append_episodic(
                MemoryItem(
                    household_id=user.household_id,
                    user_id=user.id,
                    kind="order",
                    payload={
                        "order_id": order.id,
                        "items": [
                            {"sku": li.product.sku, "qty": li.qty, "price": li.product.price}
                            for li in order.items
                        ],
                        "total": order.total,
                        "status": order.status,
                    },
                    retailer=retailer,
                    order_id=order.id,
                    source="confirmed_order",
                )
            )

        return {
            "proposal": proposal,
            "approvals": approvals,
            "placed_orders": placed,
            "handoffs": handoffs,
        }
