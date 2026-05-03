# ClawShop — Product Requirements Document

**Working name:** ClawShop
**Owner:** PM (TBD)
**Status:** Draft v0.1 — planning
**Last updated:** 2026-04-21
**Related docs:** `user-stories.md`, `brainstorm.md`

---

## 1. Executive Summary

ClawShop is an open, cross-retailer, 24/7 personal-shopper agent built on the OpenClaw framework. It watches prices, auto-reorders staples, and assembles carts across Walmart, Kroger, Amazon, and more — with a user-approval gate on every purchase.

Where Walmart's **Sparky** (consumer) and **Marty** (partner/seller) are walled-garden and single-retailer, ClawShop is retailer-agnostic and household-operations-first. We run while the user sleeps; we ask before we spend; we remember the household's real life.

**MVP target:** shippable in ~8 weeks by 2 ICs + 1 TL. Chat intake (web + SMS), three retailers (Walmart, Kroger, Amazon), cross-retailer price compare, approval gates, one autonomous behavior (price-drop watchlist).

---

## 2. Vision & Positioning

### 2.1 One-line pitch
A 24/7 personal shopper that hunts deals, reorders staples, and fills carts across every retailer you already use — so you approve, not browse.

### 2.2 Positioning statement
> For busy multi-retailer households, **ClawShop** is the always-on personal shopper that hunts deals, auto-reorders staples, and negotiates your cart across every retailer — unlike Sparky or Rufus, which only shop their own store.

### 2.3 Three pillars
1. **Open & cross-retailer.** One agent, every cart.
2. **Always-on, not always-asking.** 24/7 watching with approval gates, not a chatbot you have to open.
3. **Your data, your memory.** OpenClaw long-term memory is portable; preferences don't belong to a retailer.

### 2.4 Why now
Sparky (2025) proved consumers want agentic shopping. Rufus is default on Amazon mobile. Stripe + OpenAI + Shopify are shipping the Agentic Commerce Protocol. Virtual-card issuance (Stripe Issuing, Privacy.com) makes safe agent spend possible. Every incumbent is walled — the open slot is unfilled.

---

## 3. Personas & Target Users

### 3.1 Maya Okonkwo — "The Logistically-Loaded Household CFO"
- **38, Queens NY. Hybrid hospital billing analyst. Two kids under 6.**
- Reorders the same ~14 grocery staples every 10 days across Target, H-Mart, and the bodega delivery app.
- Forgets Similac changed her toddler's formula SKU three months ago; panics at 10 PM.
- *Quote:* "I don't need a chatbot. I need someone who remembers that my toddler is allergic to oat milk."
- **Top JTBDs:** (a) reorder household staples before we run out, at lowest total cost; (b) assemble a weekly grocery cart that fits our diet and budget in under 60 seconds.

### 3.2 Ron Delacroix — "The SMS-Only Trust-First Shopper"
- **71, Baton Rouge LA. Widower, type-2 diabetic.** Drives a 2009 Tacoma to Piggly Wiggly twice a week.
- iPhone set up by his daughter. Reads texts; distrusts apps "that keep asking for updates."
- *Quote:* "If it can't tell me the price before it buys, I don't want it."
- **Top JTBDs:** (a) keep prescriptions and household items auto-stocked with zero missed deliveries; (b) get a clear approval summary via SMS, no app required.

### 3.3 Priya Rajagopal — "The Audit-Trail Deal-Hunter"
- **29, Austin TX. Software engineer. DINK household.** Runs three Slack channels about Costco drops.
- Will A/B test her agent against her partner's.
- *Quote:* "Show me the receipts — why did you pick this SKU over the Boka one?"
- **Top JTBDs:** (a) find cheapest source for a recipe across 3+ retailers and consolidate delivery; (b) see a diff view of candidates with rationale, one tap to override.

### 3.4 Launch ICP (beta)
Women 32-45, HHI $85-175K, 2+ kids or eldercare, suburban, already splits purchases across 3+ retailers (Costco + Target + Amazon S&S + Kroger/H-E-B + Instacart overflow). Heavy users of Honey/Rakuten/Ibotta; active in r/couponing, TheKrazyCouponLady, Ibotta Reddit communities.

**Wedge use case:** "Diapers, formula, and dog food across Costco/Target/Amazon — tell me who's cheapest this week after coupons and reorder before we run out." High-frequency, high-price-variance, emotionally painful to run out of.

---

## 4. Goals & Success Metrics

| Metric | Definition | MVP Target | 90-day Target |
|---|---|---|---|
| **Activation** | % of new users who complete one approved cart within 7 days | 40% | 55% |
| **W4 retention** | % of activated users with an approved action in week 4 | 30% | 45% |
| **Approval rate** | approved / proposed actions (too low = agent is wrong; too high = agent is too conservative) | 70% | 75% |
| **Rejection-to-learning rate** | % of rejections that change a future recommendation within 14 days | 60% | 75% |
| **Assisted GMV per MAU** | $ of approved orders per monthly active user | $60 | $120 |
| **Time-to-approval p50** | seconds from push to user decision | < 90s | < 60s |
| **Order placement success** | successful placements / attempted checkouts | ≥ 95% | ≥ 98% |

### 4.1a Habit Loop Metrics

| Metric | Definition | MVP Target | 90-day Target |
|---|---|---|---|
| **Sunday Ritual completion** | % of active users who approve or edit the weekly Sunday cart proposal | 50% | 65% |
| **D14 retention** | % of activated users with an approved action in week 2 | 45% | 60% |
| **Savings Ledger share rate** | % of MAU who share their monthly savings card | 5% | 12% |
| **Referral activation rate** | % of referred sign-ups who complete onboarding within 7 days | 30% | 45% |

Sunday Ritual completion is the leading indicator of D30 retention. If it falls below 50% in week 2, that is a Sev-2 signal regardless of activation numbers.

**Guardrail metrics (never compromise):**
- Allergy-retrieval miss rate = 0.
- Unauthorized-spend incidents = 0 (any bypass of the Approval Service is a Sev-1).
- Memory poisoning false-commit rate = 0.

---

## 5. MVP Scope

### 5.1 In
- Chat intake over **web** and **SMS/iMessage** via OpenClaw User Gateway.
- Three retailer integrations: **Walmart** (Tier B deep-link + prefilled cart), **Kroger** (Tier B, cart API), **Amazon** (Tier D search + handoff).
- **Cross-retailer price comparison** on a single list (delivered cost, not sticker price).
- **Long-term memory:** dietary, allergies (pinned), brands, sizes, household size, delivery address, cadence.
- **Action Approval checkpoint** before any cart submission or subscription change.
- **One autonomous behavior:** price-drop watcher on user watchlist (max 5 SKUs in MVP; expands to 20 via referral mechanic).
- **Sunday Ritual:** weekly proposed-cart digest delivered in the user's Sunday morning window (7-10 AM, user-set); one-tap approve / edit / skip; silence never ships.
- **Savings Ledger:** running household savings counter (approved spend vs. single-retailer full price); shareable monthly card; referral unlock — share your savings card to expand watchlist from 5 to 20 SKUs.
- **"The Shelf"** memory UX: inspect, edit, delete, export, freeze.
- **Recovery flow:** 3-button (Return / Keep+credit / Keep+update-memory).
- **Virtual cards** via Stripe Issuing; no PAN in our systems.
- **Weekly email digest** of watches, learned preferences, and proposed actions.

### 5.2 Out (explicitly)
- Native full-API checkout (Tier A) on retailers that won't allow it (Amazon, consumer Walmart).
- Browser-automation Tier C (defer to V3, opt-in only).
- Mobile native apps (web + SMS + email cover it).
- Voice/smart-speaker (approval UX too risky in voice-only).
- Recipe generation, meal planning, nutrition scoring.
- Reseller/pro-buyer tooling, bulk ordering, tax handling.
- EBT/SNAP routing (regulatory, partner-only).
- Target, Instacart, local grocers (V2+).
- Returns orchestration beyond the 3-button recovery.

---

## 6. Key User Flows

### 6.1 First-run onboarding (memory bootstrap in < 4 min)
1. Sign in → single prompt: "Paste/forward a recent grocery or Amazon receipt, or tell me 3 things you bought last week."
2. Agent extracts candidate memory atoms (brand, size, store, cadence) from receipt.
3. User reviews a 10-item "Is this you?" card — toggles **Keep / Drop / Fix**.
4. Two contextual follow-ups (household size, dietary flags).
5. Agent proposes a **watchlist**, not a shopping list: "I'll watch these. Nothing buys itself yet."
6. User sets their **Sunday Ritual window** (7, 8, 9, or 10 AM local).
7. **Exit state:** ~15 memory atoms committed, Sunday window set, zero purchases authorized. **Shopping is gated until Shelf is confirmed** — no cart proposals until ≥ 15 atoms committed and at least one watchlist item is active.

### 6.2 Proactive approval flow ("milk at Target")
1. Watcher detects price drop within user preference window.
2. Policy check: total < pre-approved threshold AND retailer pre-trusted?
   - **Yes:** batch into next scheduled cart with notice.
   - **No:** explicit approval.
3. Push/SMS: "Milk (Horizon Organic 1gal) $3.19 at Target, down from $4.79. Add 2 to Saturday order? Reply Y / N / LATER / ONLY 1."
4. **4-hour response window.** No reply = do nothing. Silence never approves.
5. On Y: item added; confirmation with **undo link** valid until cart locks.
6. Post-commit: receipt card logs decision and reasoning trail ("why" affordance).

### 6.3 Recovery flow (wrong item ordered)

1. User: "You got the wrong laundry pods."
2. Agent replies with exact memory + rule used: "I chose Tide Free & Gentle based on your March note about sensitive skin."
3. Three one-tap actions: **Return + refund** / **Keep + credit** / **Keep + update memory**.
4. If memory error: surface the bad atom, offer **Delete** or **Rewrite**.
5. Single-line apology. No groveling. Autonomy dial drops one notch; restored after 3 successful orders.

### 6.4 Sunday Ritual (weekly habit anchor)
The primary recurring touchpoint. Designed to be expected, brief, and low-friction — like a standing calendar invite the user is glad to receive.

1. Every Sunday in the user's window (7-10 AM local, user-set at onboarding), ClawShop assembles a proposed weekly cart from memory atoms + active watchlist + prior order cadence.
2. Digest card delivered via SMS + web push: line-item view with retailer allocation, total cost, vs-last-week delta. Example: "Your week: 11 items, $78.20 across Kroger + Amazon. Diapers moved from Target — $3.40 cheaper at Kroger this week."
3. **One-tap options:** SEND (approve all) / EDIT (open Shelf) / SKIP (nothing ships this week).
4. Silence = nothing ships. No countdown timers, no urgency nudges, no guilt pings.
5. On SEND: carts queued per retailer; approval gates fire per §12 policy (any cart exceeding threshold triggers individual approval per retailer, not a single all-or-nothing).
6. Post-settlement: **Savings Ledger** increments by the week's savings vs. single-retailer full-price equivalent.
7. **Failure mode:** if ClawShop cannot assemble a meaningful cart (fewer than 5 items with confidence, or watchlist is empty), it sends: "Nothing to propose this week. Reply ADD to tell me what to watch." Does not send empty proposals.

### 6.5 Savings Ledger
A persistent household savings counter — the primary sharing and referral surface.

1. Displayed on the main screen and in every Sunday Ritual digest: "ClawShop has saved your household **$X** since [join date] — **$Y** this month."
2. Savings calculated as: actual approved spend vs. equivalent single-retailer full-price basket (Kroger shelf price used as baseline; methodology disclosed in UI).
3. Monthly savings card: auto-generated image, shareable to Instagram Stories, iMessage, and SMS. Designed to be readable as a screenshot. Includes referral link.
4. **Referral mechanic:** a referred user who completes onboarding → both parties' watchlist expands from 5 to 20 SKUs. No cash, no subscription discount — the unlock is functional and directly relevant to the product.
5. Savings are net of affiliate commissions. We never inflate the number by hiding affiliate take. Affiliate-purity rule: disclosed, never upcharged, never inflated.

---

## 7. Functional Requirements

### 7.1 Intake & intent
- Accept free-text requests over web chat, iMessage/SMS, email reply, and web form paste (e.g., recipe URL).
- Classify intent: `chat`, `watcher_wake`, `webhook`, `scheduled_reorder`, `approval_reply`, `sunday_ritual`.
- Respond with a structured proposal (cart) or clarifying question — never silently act without user-visible state.

### 7.2 Memory
- **Structured preferences:** typed KV (size, brand, dietary, allergy, budget, cadence, schedule).
- **Episodic:** events (orders, returns, ratings, rejections) with embeddings + structured tags.
- **Semantic:** distilled claims ("Maya prefers organic produce"), versioned with provenance.
- **Household scope:** shared vs per-user-private.
- **Write gate (see §11.2):** four-gate commit policy.
- **User-facing surface:** The Shelf (inspect, edit, delete, freeze, export, full-wipe-with-cooling-off).
- **Retrieval:** hybrid structured + vector, with allergy + active-order hard-pins.

### 7.3 Approval service
- Every state-changing tool call passes through the Approval Service.
- Policy rules (declarative, versioned, Rego-style): cost thresholds, merchant trust tier, category rules (alcohol, pharmacy, firearms, gift cards), time-of-day, novelty (new address/merchant).
- Channel fallback: push → SMS → chat → email, with 90s per tier.
- Deep-link approval URL is a single-use, device-bound JWT, 10-min TTL.
- Batching default: **one approval per cart**, not per line item. Flagged items escalate individually.
- Timeout default: 30 min → `denied`. 5 min for perishable price-drops.
- Progressive autonomy: 5 trust tiers (T1 approve-every → T5 auto-reorder-staples-under-$X). User-set only.

### 7.4 Retailer execution
- Four-tier checkout strategy (A full API, B deep-link + prefilled cart, C browser-automation opt-in, D cart-link handoff).
- MVP decision order: A → B → D. C only for users who explicitly opt-in per retailer.
- Adapter contract (every adapter implements): `search`, `getProduct`, `buildCart`, `priceCart`, `checkout`, `getOrder`, `cancel`, plus `capabilities()` bitmask.
- Error taxonomy standardized: `AUTH`, `RATE_LIMIT`, `OUT_OF_STOCK`, `PRICE_CHANGED`, `TOS_BLOCKED`, `CAPTCHA`, `UPSTREAM_5XX`, `UNSUPPORTED`, `USER_ACTION_REQUIRED`.

### 7.5 Payments
- No PAN in our systems. Stripe Issuing (primary), Privacy.com (backup).
- One virtual card per (user, merchant) with hard cap = approved amount + 7% slack; auto-closes after N days or first settle.
- PCI scope: vault service only. Rest of fleet out of scope.
- Agent holds an opaque `paymentToken`. PaymentVault is the only component that resolves token → card.

### 7.6 Watchers
- User-configurable predicate DSL per SKU (`price < $X`, `back_in_stock`, `deal_tag in [...]`, `% drop ≥ X`).
- Cooldown per watcher to prevent spam.
- Webhook-first, adaptive-poll fallback.
- **No LLM on the watcher hot path.** Predicate evaluates in pure Python against cached retailer state. LLM wakes only when predicate fires AND cooldown passed AND Haiku-tier "is this worth pinging?" gate passes.

### 7.7 Recovery
- Three one-tap correction actions: Return + refund / Keep + credit / Keep + update memory.
- Memory errors surface the offending atom with Delete / Rewrite affordances.
- Autonomy dial drops one tier on error; restored after 3 successful orders.

---

## 8. Non-Functional Requirements

| Area | Requirement |
|---|---|
| **Latency (chat)** | p50 ≤ 4s, p95 ≤ 10s for synchronous responses |
| **Latency (approval delivery)** | p95 < 5s from policy-fire to user-device |
| **Retailer call latency** | p95 < 2s (Tier A/B APIs), < 12s (Tier C browser) |
| **Order placement success** | ≥ 98% for Tier A/B |
| **Availability** | 99.5% for gateway + approval service in MVP |
| **Cost per turn** | chat ≤ $0.04, watcher-wake ≤ $0.005, webhook ≤ $0.01, reorder ≤ $0.02, sunday-ritual ≤ $0.03 per user |
| **Cost per watched item** | ≤ $0.02/day steady-state |
| **Security** | PCI scope minimized; vault-only PAN; PII encrypted at rest and in transit |
| **Privacy** | CCPA/CPRA + GDPR compliant; data export + delete on request |
| **Accessibility** | WCAG AA on all visual surfaces; SMS path fully functional without app |

---

## 9. System Architecture (overview)

### 9.1 Component diagram
```
                         [ OPENCLAW ]                                  [ OURS ]
 User ──► User Gateway ──► Orchestrator Agent ──► Sub-agents ──► Retailer Adapter Layer ──► Retailers
 (chat,      (stream,          (planner)          ├ Search         ├ Walmart API
  app,       multi-modal)          │              ├ Compare        ├ Amazon PA-API (search only)
  SMS)                             │              ├ Checkout       ├ Kroger API
                                   │              └ Watcher        └ Generic fallback
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
        [Memory Store]    [Approval Service]    [Payment Vault]
         OpenClaw LTM +    OpenClaw HITL +       ours (tokens,
         our write-gate    our policy engine     virtual cards)
                                   │
                                   ▼
                             [Event Bus / Scheduler] ── cron, webhooks, price feeds
```

### 9.2 Trust boundaries
- **Gateway boundary:** user-facing channel adapters.
- **Agent runtime boundary:** untrusted tool output enters here; schema-validated before agent sees it.
- **Action surface boundary:** every state-changing tool call crosses Approval Service.
- **Payment vault boundary:** PAN never returned to agent.

### 9.3 Orchestration pattern
**Multi-agent with a lightweight planner.** Orchestrator + 4 specialists (Search, Compare, Checkout, Watcher). Rationale: single mega-prompt collapses under context for 5 retailers + memory + approvals; specialists keep prompts small and enable per-role model routing.

- Planner produces 3-7 step plan, dispatches each step as `{goal, constraints, budget_tokens, budget_dollars}`.
- Bounded: max 12 steps, max 3 re-plans, hard timeout.
- Reflection: cheap critique model gates draft output.
- 24/7 cost discipline: watchers are cron + cheap heuristics, not always-on agents.

### 9.4 Model routing
| Step | Model |
|---|---|
| Intent classify | Haiku |
| Watcher "is this interesting?" | Haiku |
| Memory candidate extract | Haiku |
| Memory dedup/conflict | Sonnet |
| Planning (chat) | Sonnet |
| Tool-arg filling | Sonnet |
| Ambiguous judgment, cross-retailer, money > $50 | Opus |
| Reflection / self-check | Haiku |
| Nightly episodic → semantic distillation | Sonnet (batch) |

### 9.5 Tech stack
- **Language:** Python (agent + adapters), Go (Approval Service + adapter gateway).
- **LLMs:** Claude (Haiku / Sonnet / Opus), routed per step.
- **Vector store:** pgvector on Postgres.
- **Queue / workflow:** Temporal (durable agent workflows, retries, human-in-loop timers).
- **Events:** Redis Streams (webhooks), Kafka (audit/obs).
- **DB:** Postgres (structured + pgvector + append-only audit).
- **Deploy:** Kubernetes; adapter scrapers in a segregated node pool with egress proxy.

---

## 10. Data Model

| Entity | Purpose |
|---|---|
| **User** | Identity, auth, contact channels |
| **Household** | Group of users sharing preferences/budget |
| **Preference** | Typed structured memory (key, value, confidence, version, ttl) |
| **MemoryItem** | Episodic event (embedding, tags, provenance, version) |
| **SemanticClaim** | Distilled claim with support_count + provenance list |
| **Order** | Line items, retailer, status, payment_token ref, approval ref |
| **WatchedItem** | SKU, predicate DSL, cooldown, next_check_at |
| **ApprovalRequest** | Action payload, policy hits, decision, user response, ts |
| **RetailerAccount** | Per-user per-retailer encrypted credentials + session state |
| **PaymentToken** | Opaque handle → Stripe Issuing/Privacy.com card (vault-only) |

---

## 11. Memory Policy (detailed)

### 11.1 Stores
- `preferences(household_id, user_id, key, value, type, confidence, source_turn_id, updated_at, ttl_days)` — typed KV, unique per key.
- `episodic(id, household_id, user_id, ts, kind, payload, embedding, retailer, order_id)` — events.
- `semantic(id, household_id, user_id, claim, embedding, support_count, last_seen, confidence, provenance)` — distilled.
- `household(household_id, key, value, scope, owner_user_id)` — scope: `shared | private_to_owner`.

### 11.2 Write gate — four checks, all must pass
1. **Evidence threshold.** Observed in ≥2 distinct sessions OR imperative language ("always", "never", "I'm allergic to").
2. **Classifier pass.** Small model labels candidate as `preference | one-off | noise`; only `preference` proceeds.
3. **Conflict check.** If contradicts existing memory, route to Approval Service for user confirmation. No silent overwrite.
4. **Provenance.** Every MemoryItem carries `session_id`, supporting utterance, timestamp. Memories are versioned; hard-delete disabled.

### 11.3 Commit thresholds
- Confidence ≥ 0.85 and not money-affecting → auto-commit.
- 0.6-0.85 → commit as `provisional`, surface next turn for user confirmation.
- < 0.6 → drop, keep in episodic only.
- Allergy / medical → always user-confirm, regardless of confidence. TTL = null. Never decays.

### 11.4 TTL / decay by type
- Brand preference: 180d
- Schedule / cadence: 90d
- Budget: 365d
- Allergy / medical: ∞ (never decays)
- Semantic `confidence *= exp(-Δt/τ)` on read; re-supported claims reset.

### 11.5 Poisoning defense
- **Source-trust tag** on every candidate. Only `source in {user_turn, confirmed_order, user_approved_tool_output}` can write to `preferences` or `semantic`. Product descriptions, reviews, emails, web pages → `source=untrusted`, `episodic`-only.
- **Prompt-injection detector** on all untrusted text before reaching extract.
- Tool allowlist is static config — not memory-derived. "Always order from X" cannot rewrite the retailer allowlist.
- Any memory write that would change a money-bearing parameter (payment method, shipping address, retailer preference) is forced to user-confirm regardless of confidence.

### 11.6 Retrieval
- Token budget: 30% of turn tokens, split 40/30/20/10 across preferences / semantic / episodic / household.
- Hard-pins: active orders, allergies, current budget cap — never evicted.
- Recency decay on score; dedup at pack time.

---

## 12. Approval Policy (detailed)

### 12.1 Rules (declarative, order-evaluated)
```
require_approval if
  action.cost > user.auto_approve_limit OR
  action.retailer not in user.trusted OR
  action.category in {alcohol, pharmacy, firearms, gift_card} OR
  action.delta_from_estimate > 15% OR
  action.shipping_address not seen in 30d OR
  time_of_day in [02:00, 06:00]
```

### 12.2 Channel fallback (ranked)
Push (APNs/FCM) → SMS (Twilio) → chat reply in-thread → email. 90s per tier. Deep-link opens a signed, single-use approval URL (JWT, 10 min TTL, device-bound).

### 12.3 Batching
- Default: 1 approval per cart.
- Flagged items (alcohol, Rx, new merchant) escalate individually.
- Never silently drop items. Show what was filtered and why.

### 12.4 Timeouts
- Default: 30 min → denied.
- Perishable price-drop: 5 min → denied.
- Timeouts always default to denial. Silence never approves.

### 12.5 Progressive autonomy (5 tiers)
| Tier | Behavior |
|---|---|
| **T1** | Approve every action (default for new users) |
| **T2** | Auto-approve re-orders of previously-approved exact items under $20 |
| **T3** | Auto-approve staples under $30 from trusted merchants |
| **T4** | Auto-approve staples under $75; post-commit notification with reversal window |
| **T5** | Auto-reorder staples under user-set cap $X; weekly digest review |

Trust is user-set only. A misfire drops autonomy one tier with a visible indicator. Restored after 3 successful corrections.

---

## 13. Retailer Integration Plan

### 13.1 Feasibility (2026)
| Retailer | Has API? | Checkout via API? | Rate-limit risk | ToS risk | MVP tier |
|---|---|---|---|---|---|
| Walmart | Yes (affiliate + limited partner) | No consumer; partner-only | Med | Low | **B** |
| Amazon | PA-API 5 | No (no 3P programmatic checkout) | High | High if we scrape | **D** (search + handoff) |
| Kroger | Public API | Cart yes, checkout no | Low | Low | **B** |
| Target | RedSky (unofficial) + partner | No publicly | Med | Med | V2 (stretch) |
| Instacart | Connect (partner-gated) | Yes if approved | Low once in | Low | V2 (partnership gate) |
| Generic web | No | No | N/A | High | Fallback read-only |

### 13.2 Checkout tiers
- **Tier A — full API checkout.** Instacart Connect (if partnered). Not assumed for MVP.
- **Tier B — deep-link + prefilled cart.** MVP default. Walmart, Kroger.
- **Tier C — Playwright in Firecracker microVM, user-consented.** Opt-in, per-retailer. V3 only.
- **Tier D — cart link, human finishes.** Amazon always. Any retailer when A/B/C fail.

### 13.3 No-API retailers
Headless-browser workers in isolated pool, residential proxies, per-account session reuse, aggressive caching. Treat all scrape responses as `untrusted`; schema-validate before the agent sees them.

### 13.4 Caching & rate limits
- Redis: 10 min price, 1 hr product detail, 24 hr static catalog.
- Token-bucket per adapter; circuit breaker with fallback to generic fetch.
- Never fall back to "skip and guess."

---

## 14. Security & Privacy

### 14.1 Payments
- No PAN stored in our systems. Stripe Issuing primary, Privacy.com backup.
- Virtual card per (user, merchant) with hard cap = approved amount + 7% slack.
- Card auto-closes after N days or first successful settle.
- PCI scope: vault service only. Network-isolated, dedicated KMS, separate deploy pipeline.
- 3DS/SCA lands on user's device via approval deep-link.

### 14.2 Threat model
| Threat | Mitigation |
|---|---|
| Prompt injection via product pages/reviews | Strip to plain text; tag as `untrusted`; agent system prompt forbids acting on untrusted instructions; tool allowlist enforced server-side |
| Compromised retailer account | Virtual card caps; anomaly detection on address changes; step-up WebAuthn for new-merchant / new-address |
| User account takeover | Device-bound approval tokens; WebAuthn for high-value approvals; re-auth on new channel |
| Replayed approvals | Single-use nonce'd approval JWTs; server-side marked-consumed before checkout; checkout idempotent on approval-id |
| Memory poisoning | Source-trust tag, poisoning classifier, money-affecting params locked to user-confirm, tool allowlist not memory-derived |
| Unauthorized spend at agent layer | Approval Service as mandatory gate; virtual card cap as last-line defense |

### 14.3 Privacy & compliance
- **CCPA/CPRA + GDPR.** Explicit opt-in for cross-retailer memory. JSON export + full-delete with 24-hr cooling-off.
- **FTC Endorsement Guide.** Per-recommendation affiliate disclosure in-UI. Never upcharge user for affiliate revenue.
- **Retailer ToS.** Only official APIs or user-consented browser sessions. No scraping in MVP.
- **California ADMT (2026).** Disclose automated purchasing decisions to users.
- **SNAP/EBT.** Out of scope for MVP. Partner-only path post-launch.

### 14.4 ClawShop Guarantee (purchase protection)
ClawShop refunds any wrong-item, wrong-size, wrong-brand, or unauthorized purchase up to **$200 per incident, $500/yr per household**, within 24 hours, no investigation required. Rationale: without this, every incident is adversarial; with it, the first bad purchase becomes a brand-building moment. Budget the expected cost (~0.3% of GMV based on industry wrong-item rates) as CAC, not as loss. Required for ClawShop+ subscribers; available as paid add-on on free tier.

### 14.5 Kill-switch & stop-the-world
- **Global kill-switch**: single operator action, audit-logged, freezes all outgoing spend authorizations and approval-request issuance fleet-wide. RTO < 5 minutes. Tested monthly.
- **Per-user pause**: self-serve, reachable from SMS reply "PAUSE" or in-chat. Instant.
- **Per-merchant block**: if a retailer exhibits compromise signals, operator can freeze all spend to that merchant without a deploy.

### 14.6 Per-approver identity binding
SMS approvals are bound to **approver identity**, not household phone number. Each household approver enrolls a short PIN (free tier) or device-bound WebAuthn (ClawShop+). An approval ≥ $100 or for a new merchant requires the PIN/WebAuthn step even if sent to a device already in-session. Closes the kid-replies-Y and shared-device-takeover failure modes.

---

## 15. Observability & Evals

### 15.1 Event bus
Structured JSON events, schema-versioned, one Kafka bus:
`AgentTurn`, `ToolCall`, `ApprovalRequest`, `ApprovalDecision`, `RetailerCall`, `CartBuilt`, `OrderPlaced`, `OrderSettled`, `PaymentAuthorized`, `MemoryWrite`, `WatcherFired`.

### 15.2 Dashboards
- **Eng:** retailer call p50/p95/p99, error taxonomy breakdown, vault auth latency, Kafka lag, watcher job health.
- **Product:** orders/day by retailer, approve-rate, time-to-approval, GMV, cart abandonment by tier, memory override rate.
- **On-call alerts:** order placement < 95% over 15m, approval delivery < 98%, `TOS_BLOCKED` spike, vault 5xx, issuer decline > baseline+3σ.

### 15.3 SLOs
- Approval delivered p95 < 5s
- Retailer call p95 < 2s (API) / < 12s (Tier C)
- Order placement success ≥ 98% (Tier A/B)
- Availability 99.5% (MVP gateway + approval)

### 15.4 Eval harness
Golden sets under `evals/`, run on every PR + nightly:
- `tool_decisions.jsonl` — (trigger, memory snapshot, expected tool+args OR "ask user" OR "no-op"). ~300 scenarios.
- `memory_writes.jsonl` — (turn, expected candidates, commit/provisional/drop verdict).
- `poisoning.jsonl` — adversarial product texts, emails, prior-turn injections.
- `retrieval.jsonl` — (user, trigger, expected must-include memory ids).

**Correctness:**
- Tool decision: exact tool + args (schema-aware differ, addresses/prices normalized). Ask-user vs act is a hard class; false "act" weighted 5× false "ask".
- Memory write: verdict class match; confidence within 0.15 of label.
- Retrieval: must-include recall@budget = 1.0 for allergies / active orders (hard fail if missed); nDCG for the rest.

**Regression gates:**
- Tool-decision accuracy drop > 1pt → block merge.
- Any allergy retrieval miss → block merge.
- Any poisoning false-commit → block merge.
- Track per-model-tier so a router change surfaces cleanly.

**Shadow eval:** mirror 1% of prod traffic, diff decisions, alert on divergence.

### 15.5 Red-team scenarios (monthly)
Prompt injection in product titles/reviews; memory poisoning via crafted user messages; infinite re-plan loops (caught by step budget); wrong-account purchase (caught by approval + virtual-card merchant lock); adapter returning attacker-controlled JSON; replayed/stale approval tokens; **Approval Service bypass chaos drill** — the last-line virtual-card cap must hold even if everything upstream is compromised.

---

## 16. Marketing, Pricing & GTM

### 16.1 Pricing hypothesis
- **Free tier:** 1 active watch, manual approvals, basic reorder.
- **ClawShop+ at $14.99/mo or $129/yr:** unlimited watches, auto-reorder with spend caps, coupon stacking, household sharing (up to 4 seats), priority deal alerts, purchase guarantee (see §14.4).
- **Why $14.99, not $7.99:** ICP (HHI $85-175K, $40-80/mo in grocery savings) pays $14.99 without friction. At $14.99, LTV:CAC clears 4-5× versus 2-3× at $7.99. $7.99 under-prices the value and doesn't cover CS load on money-touching products.
- **Stacked revenue, but don't plan on it:** retailer affiliate commissions (Amazon 1-4%, Target 1-8%, Walmart via Impact 1-4%, Kroger <1%). Realistic month-18 mix is **70 sub / 30 affiliate**, NOT 50/50. Amazon and Walmart will revoke or throttle our affiliate tags as our volume grows (same playbook they ran on Jet, Honey, Capital One Shopping).
- **Critically:** never upcharge user for affiliate. Show net-of-affiliate price, or rebate. Affiliate purity is the trust moat post-Honey/PayPal 2024 exposé — costs ~30% of gross affiliate take vs. scummy version; keep it and market it hard.

### 16.1a Unit economics (realistic)
| Line | Value | Source |
|---|---|---|
| Blended CAC (Reddit + TikTok + PR) | $45-70 fully loaded | Marketing, Y1 blended |
| Subscription GPM | ~70% at $14.99 | After Stripe, SMS, infra |
| COGS per household/month (floor) | $1.20-2.00 LLM + $0.30 virtual card + $0.40 infra = **~$2** | IC #1 model routing; IC #2 vault |
| CS load allowance | 4-10× non-money-product baseline | Risk register §ops |
| Affiliate per $400/mo assisted GMV | $10-11/mo blended, trending to zero as Amazon/Walmart pull APIs | Marketing analysis |
| 25-mo customer lifetime | at 4% monthly churn | Industry benchmark for this ICP |
| LTV at $14.99 | ~$260 | Sub + residual affiliate |
| LTV:CAC | 4-5× at $14.99, 2-3× at $7.99 | Marketing |

Break-even per household lands month 4-5 at $14.99; month 9+ at $7.99. **$14.99 is the only price that works at our CS cost reality.**

### 16.2 Go-to-market — first 1,000 users
- Seed r/couponing, r/Frugal, r/Costco, r/Target, BuyNothing Facebook groups with a "deal-hunter leaderboard."
- Partner with 10-20 mid-tier TikTok grocery-haul creators ($10-100K followers) — flat fee + affiliate, "ClawShop vs my usual list" challenge.
- Integrate with TheKrazyCouponLady / Hip2Save — admin dashboard to publish watches into ClawShop.
- Seed Costco/Sam's forums — bulk-buyers are our highest-AOV cohort.
- "Open Sparky" narrative in tech press (The Verge, TechCrunch, Retail Dive).

### 16.3 Differentiators vs incumbents
| Capability | Sparky | Rufus | Instacart | **ClawShop** |
|---|---|---|---|---|
| Cross-retailer price compare | No | No | No | **Yes** |
| 24/7 price-drop + restock watch | Walmart only | No | No | **Yes** |
| Coupon stacking (manufacturer + store + card-linked) | Limited | No | No | **Yes** |
| Auto-reorder with spend-cap approval | Walmart-only | No | Subscriptions only | **Yes, cross-retailer** |
| User-owned portable memory | No | No | No | **Yes (OpenClaw)** |
| EBT/SNAP-aware routing | Walmart only | No | Partial | V2 |
| Open to developer extensions | No | No | API only | **Yes (OpenClaw plugins)** |

### 16.4 Business viability — retail industry perspective

#### Does retail want this? — split, hostile at the top
| Stakeholder | Stance | Rationale |
|---|---|---|
| **Walmart** | Hostile | Sparky + agentic checkout in pilot; ~18-month tolerance window before throttle/ToS action (Jet / Honey / Capital One Shopping playbook) |
| **Amazon** | Actively hostile | ToS already prohibits automated purchasing; sued Nimble; Rufus going native checkout 2026. Plan for affiliate-tag revocation |
| **Target** | Friendly | Distant #3 in digital, needs incremental demand, small Roundel ad business — good early API partner |
| **Kroger** | Friendly | Boost membership stalling, thinnest digital GMV of the majors. Will take our calls |
| **Costco** | Irrelevant | No API, no affiliate worth anything, allergic to third parties. Skip |
| **Instacart** | Frenemy | Will take Connect referrals now; Instacart-native agent on roadmap. Renting runway |
| **CPG brands (P&G, Unilever, Kraft Heinz)** | Terrified, 2-yr sales cycle | Agents collapse shelves into spec sheets — kills brand equity. Eventually they'll pay us for agent-facing placement; org structure not ready in 2026 |
| **Payment rails (Visa, Mastercard, Stripe)** | Allies | Visa Intelligent Commerce, Mastercard Agent Pay, Stripe+OpenAI ACP all want agent volume — clean win |
| **Retail media networks (Walmart Connect, Amazon Ads, KPM)** | Won't partner | Agents torch their highest-margin sponsored-product inventory. Assume zero cooperation |

**Net verdict:** two biggest players structurally against; #3-#5 tier plus payment rails pulling for us.

#### Does the business model work? — lifestyle business yes, venture-scale only with act-two
- **Subscription ($14.99/mo)** — LTV:CAC clears 4-5×, break-even month 4-5. $7.99 was under-priced for the CS load.
- **Affiliate durability is a mirage** — 50/50 mix by month 18 is not plausible. Real trajectory: 70/30 sub-heavy, with affiliate trending to zero as Amazon/Walmart pull APIs. Do not build the model on affiliate durability.
- **COGS floor ~$2/household/month** (Haiku-routed LLM + Stripe Issuing + infra).
- **Honey-purity moat** — affiliate-disclosed, no upcharge, no coupon-swap scummery. Costs 30% of affiliate take; buys the trust moat the post-Honey ICP demands.
- **No network effects** — linear SaaS grind. Consumer ceiling: $20-40M ARR.
- **Defensible wedge** — cross-retailer neutrality + user-owned portable memory. Walmart structurally cannot honestly recommend Kroger.
- **Venture-scale exit:** B2B agent infrastructure white-label to retailers (see §17 V4). Consumer business is the proof-of-ops for the B2B sale.

**Verdict:** clears lifestyle bar comfortably. Clears venture-scale only if we commit to the B2B act-two in year 2.

---

## 17. Roadmap

### V1 — MVP (8 weeks, consumer)
Chat intake (web + SMS), 3 retailers (Walmart, Kroger, Amazon-handoff), cross-retailer comparison, approval gates, price-drop watchlist (5-SKU cap), Shelf memory UX, 3-button recovery, virtual-card vault, **Sunday Ritual** (§6.4 — weekly proposed-cart digest, primary habit anchor), **Savings Ledger** (§6.5 — household savings counter + referral mechanic), **ClawShop Guarantee** (purchase protection, §14.4), **global kill-switch**, **deterministic allergen/age-gated denylist**.

### V2 — 90 days (consumer + partnership)
Auto-reorder staples with spend caps (T3 tier default), household sharing with per-approver identity binding, Target + 2 local grocers, rejection-learning loop, browser extension (price capture + "watch this"), Instacart Connect if partnership lands. **Target: sign data/API partnership with at least one of Walmart / Kroger / Target** — turns retailer-hostility from existential to managed.

### V3 — 180 days (consumer maturity)
Recipe-to-cart, native Tier A checkout via stored payment where APIs allow, pro-buyer mode with bulk pricing, opt-in Tier C browser-automation checkout (with dedicated on-call rotation), Agentic Commerce Protocol adoption, smart-speaker surface (read-only digest, no voice-approval for spend).

### V4 — Act Two: B2B agent infrastructure (12-18 months)
White-label the ClawShop stack (agent runtime, memory subsystem, approval service, virtual-card vault) for retailers who need agentic-commerce but can't build it in-house — **Kroger, Target, mid-tier grocers, drug chains, specialty retailers**. Rationale: consumer path caps at $20-40M ARR (Marketing verdict); B2B is where venture-scale lives. The retailers Walmart and Amazon are about to crush with in-house agents are our ICP for B2B.

**Why we can win B2B:** (a) we'll have 12-18 months of production-scale agentic-commerce ops experience; (b) cross-retailer neutrality in the consumer product proves we can be trusted as a neutral infrastructure vendor; (c) OpenClaw as the underlying primitive gives us an open-source story that closed-source incumbents (Sparky, Rufus) can't match.

**Signal to trigger:** consumer metrics plateau at $8-15M ARR AND at least one Tier-2 retailer signals appetite in beta discussions.

### V5 — Portable agent rights (speculative, 24+ months)
Push the "your data, your memory" pillar to its logical conclusion: portable agent identity across retailers and agents, via the Agentic Commerce Protocol or successor. Positioned as the "HTTP of agent shopping."

---

## 18. Risks & Open Questions

### 18.1 Product risks
1. **Trust collapse on one bad auto-order.** A single wrong $200 charge kills retention. Default autonomy is T1 (approve-every); virtual-card cap is last-line defense.
2. **Preference cold-start.** Without 2-3 weeks of signal, recommendations are generic. Receipt-paste onboarding shortens this; open question: should we offer OAuth into retailer order history?
3. **Monetization tension.** Affiliate fees bias recommendations. We disclose and never upcharge — but do we cap affiliate share in V1 to remove even the incentive?
4. **Retailer adversarial response.** Amazon/Walmart may rate-limit or block. Do we push for partnerships, stay Tier D, or both?

### 18.2 Technical risks
1. **Scraper fragility** for Amazon/Target. Half our catalog coverage depends on DOM that changes weekly. MVP mitigates by staying Tier D on Amazon; Target deferred.
2. **Memory poisoning / drift.** One sarcastic comment becomes permanent truth. Write gate is the defense; rising correction rate is a Sev-2.
3. **Unauthorized purchase.** Prompt injection or bug bypassing Approval Service is a financial incident. Virtual-card caps are last line. Chaos-test monthly.
4. **Virtual card declines.** Retailers increasingly reject prepaid BINs (especially Amazon, Target). Expect 5-15% out of the gate. Need BIN rotation + clean retry without double-charging.
5. **Playwright Tier C at scale** (V3). Session cookies, 2FA, bot detection (Kasada, PerimeterX) — plan on-call rotation before enabling by default.

### 18.3 Open questions
- OAuth into retailer order history at onboarding — worth the privacy hit?
- First-party mobile app — do we skip it forever, or does V2 demand one?
- Agentic Commerce Protocol — commit early to Stripe/OpenAI/Shopify standard, or stay neutral until it has real volume?
- Household approval semantics — first-response wins, or both must consent over a threshold?
- Do we cap affiliate revenue in V1 to signal neutrality?

### 18.4 Regulatory watch-outs
- FTC Endorsement Guide (affiliate disclosure in every AI recommendation).
- California ADMT rules effective 2026 (disclose automated purchasing decisions).
- CCPA/CPRA + GDPR (export + delete, opt-in for cross-retailer memory).
- Retailer ToS + CFAA (no scraping without consent).
- PCI-DSS (vault-only PAN).
- USDA FNS (SNAP/EBT — partner-only, out of scope MVP).
- Antitrust optics (see Amazon vs. Perplexity Comet, late 2025).

---

## 19. Team & Timeline

**Team:** 1 PM, 1 Marketing, 1 UX, 1 TL, 2 IC eng.

**8-week MVP timeline (high-level):**
| Week | Focus |
|---|---|
| 1 | Arch spike, OpenClaw integration, Stripe Issuing POC, retailer adapter contract frozen |
| 2 | Walmart + Kroger adapters (search + cart build), memory schema + write gate v0 |
| 3 | Amazon adapter (Tier D), Approval Service + policy engine, SMS + web chat gateway |
| 4 | Orchestrator + planner, model routing, The Shelf UX v1 |
| 5 | Price-drop watcher (predicate DSL + Haiku gate), deep-link checkout (Walmart, Kroger) |
| 6 | Recovery flow, weekly digest, eval harness + golden sets |
| 7 | Red-team drills, WebAuthn step-up, virtual card chaos drill, load test |
| 8 | Closed beta (ICP cohort, 100 users), dashboards, on-call playbook |

---

## 20. Appendix — Interface Surfaces (ranked for MVP)

1. **SMS / iMessage** — universal, no install, works for Ron. Sunday Ritual and approval responses are SMS-native. Ship first.
2. **Web chat + Savings Ledger dashboard** — richer cards, Shelf UI, running savings counter, shareable monthly card.
3. **Sunday Ritual digest (SMS + email)** — weekly proposed cart with one-tap approve / edit / skip; upgraded from "recap" to "proposal." Primary habit anchor.
4. **Browser extension** (V2) — price-drop capture, "watch this" on any retailer page.
5. **Mobile native app** (V3+) — defer until web + SMS + email prove trust.
6. **Smart speaker** (V3+) — read-only digest, never voice-approval for spend.

---

*End of PRD v0.1.*
