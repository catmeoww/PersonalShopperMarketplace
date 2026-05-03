# ClawShop — vertical-slice prototype

Prototype implementation of the ClawShop personal-shopper agent described in
`docs/PRD.md`. This is a **single-process Python slice** that exercises the
PRD's load-bearing concepts end-to-end with mocks at the retailer/payment/SMS
boundaries.

| PRD section | Implemented in |
|---|---|
| §11 Memory write-gate (4 checks, allergy always-confirm, source-trust) | `clawshop/memory/write_gate.py` |
| §11.6 Retrieval with hard-pins | `clawshop/memory/retrieval.py` |
| §12 Approval Service (rules, timeout=denied, replay defense) | `clawshop/approval/` |
| §7.4 Retailer adapter contract + error taxonomy | `clawshop/retailers/` |
| §7.6 Watcher with no-LLM hot path + Haiku gate | `clawshop/watcher/` |
| §7.5 Payment vault — opaque tokens, no PAN | `clawshop/payments/vault.py` |
| §9.3 Multi-agent orchestration | `clawshop/agent/` |
| §9.4 Model routing (Haiku/Sonnet/Opus) | `clawshop/llm.py` + `clawshop/config.py` |

## Run

```bash
pip install -e ".[dev]"

# Stub mode — no Anthropic API key needed:
LLM_MODE=stub python -m clawshop demo

# Live mode — exercises real model routing per PRD §9.4:
LLM_MODE=live ANTHROPIC_API_KEY=sk-... python -m clawshop demo

# Tests:
pytest -q
```

## What the demo shows

`python -m clawshop demo` walks the Maya scenario from PRD §6.1 / user-story A1:

1. Bootstraps a household and writes seed preferences (Pampers, Peet's). The
   allergy ("oat milk") goes through the write-gate and lands as
   `needs_user_confirm` with `ttl_days=None` (PRD §11.3).
2. Sends `"we're out of diapers and coffee"` to the orchestrator.
3. Searches Walmart / Kroger / Amazon mocks in parallel; compares per item.
4. Submits one Action per retailer to the Approval Service (PRD §12.3
   batching default).
5. Issues a virtual-card token (cap = approved + 7%, PRD §7.5), checks out
   on retailers with `Capabilities.CHECKOUT`, and emits Tier-D handoff links
   for Amazon (PRD D2).
6. Runs a watcher tick on a coffee price drop. Predicate evaluates in pure
   Python; only on a fire does the Haiku-tier "is this worth pinging?" gate
   wake (PRD §7.6, F5).

## What's deliberately out of scope

Stripe Issuing, Twilio/SMS gateway, Postgres + pgvector, Temporal, Kafka,
Sunday Ritual scheduler, Savings Ledger, WebAuthn, kill-switch, real retailer
APIs, browser-automation Tier C. Each is stubbed at a clear seam so it can be
swapped in without changing the surrounding code.
