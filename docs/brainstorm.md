# ClawShop — Brainstorm Transcript

Raw perspectives from a 6-agent brainstorm session on 2026-04-21. Six agents each got the same problem brief — a 24/7 personal-shopper agent built on OpenClaw, open and cross-retailer, as the open answer to Walmart's Sparky/Marty — and each wrote from their role without seeing the others. Their voices are preserved below; contradictions and tensions are listed at the end.

**Roster**
- PM — product vision, scope, success metrics
- Marketing — retail market, positioning, GTM, pricing
- UX — personas, flows, trust & memory surfaces
- TL — architecture, orchestration, data model
- IC #1 — agent loop, tool use, memory subsystem
- IC #2 — retailer integrations, gateway, approvals, payments, observability

Synthesized outputs live in `PRD.md` and `user-stories.md`. This doc is the raw material.

---

## 1. PM — product brief

### Vision
ClawShop is a 24/7 personal shopper that hunts deals, reorders staples, and fills carts across every major retailer — so you approve, not browse. Now is the moment: Walmart's Sparky proved consumers want shopping agents, but locked them into one retailer; an open, cross-retailer agent wins on price and trust.

### Target users & top JTBDs
- **Busy parent (dual-income, 2 kids)** — reorder staples at lowest total cost; assemble a weekly grocery cart in under 60 seconds.
- **Caregiver for an elderly parent** — keep Mom's meds and adult-care items auto-stocked; get a clear approval summary from my phone.
- **Home chef on a budget** — cheapest source for a recipe across 3+ retailers; substitute out-of-stock with chef-acceptable alternatives.

### MVP — in/out
**In:** chat (web + SMS), three retailers (Amazon, Walmart, Instacart), cross-retailer compare, long-term memory, approval checkpoint, one autonomous behavior (price-drop watchlist max 20 SKUs).
**Out:** native checkout/payment, mobile apps, voice, browser extension, recipe gen, meal planning, reseller tools, local grocers beyond the core three, returns/refunds flow.

> PM note: the eng team later argued Kroger in, Instacart out for MVP because of partnership gating. See §4 and §6.

### Success metrics
- **Activation** — 40% of new users complete one approved cart within 7 days.
- **W4 retention** — 30% of activated users have an approved action in week 4.
- **Approval rate** — 70%+ (too low = agent is wrong; too high = too conservative).
- **Rejection-to-learning rate** — 60% of rejections change a future recommendation within 14 days.
- **Assisted GMV per MAU** — $120 by day 90.

### Risks & open questions
- Retailer adversarial response (rate-limit, block). Partner, scrape, or both?
- Trust collapse on one bad auto-order — is the default threshold low enough?
- Preference cold-start — OAuth into retailer order history at onboarding?
- Monetization tension — affiliate fees bias recommendations; disclose, cap, or refuse in V1?

### Roadmap
- **V1 (8w):** Chat, 3 retailers, compare, approval, watchlist.
- **V2 (90d):** Auto-reorder with caps, household sharing, Target + 2 local grocers, rejection-learning.
- **V3 (180d):** Recipe-to-cart, native checkout via stored payment, browser extension, pro-buyer mode.

---

## 2. Marketing — retail landscape, positioning, GTM

### Market landscape (2026)
- **Walmart Sparky** (launched mid-2025, expanded Q1 2026): in-app conversational shopper, reorder + recipe-to-cart + image-search, agentic checkout rolling out — but locked to Walmart.com/Walmart+ SKUs. **Marty** is the seller-side twin (listing optimization, ad bidding) for 3P Marketplace.
- **Amazon Rufus**: default on mobile app, strong on product Q&A and comparison within Amazon's catalog; still no true agentic buying, no price-drop watching across retailers, and Amazon ToS explicitly blocks third-party agents from transacting on amazon.com.
- **Instacart "Ask Instacart" + Connect API**: meal-planning and dietary-filter queries, tied to Instacart's grocery network and marked-up pricing.
- **Perplexity Shopping + OpenAI Operator / ChatGPT shopping**: horizontal agent checkout via Stripe/Shopify rails — great discovery, weak on loyalty accounts, coupons, EBT/SNAP, household-staple reorder logic.
- **Klarna AI Assistant**: 2.5M+ MAU, strong on BNPL-native discovery and price memory, but checkout-finance-first, not household-operations-first.

**The gap:** nobody runs a persistent, cross-retailer, household-operations agent that watches prices across Walmart + Target + Kroger + Costco + Amazon simultaneously, stacks manufacturer + store + card-linked coupons, and executes with user-approved spend gates. Every incumbent is walled-garden or single-session.

### Positioning statement
> For busy multi-retailer households, **ClawShop** is the always-on personal shopper that hunts deals, auto-reorders staples, and negotiates your cart across every retailer you already use — unlike Sparky or Rufus, which only shop their own store.

**Pillars:** (1) open & cross-retailer; (2) always-on, not always-asking; (3) your data, your memory.

### ICP for launch beta — "The Logistically-Loaded Household CFO"
Women 32-45, HHI $85-175K, 2+ kids or eldercare, suburban, already splitting purchases across 3+ retailers (Costco bulk + Target weekly + Amazon S&S + Kroger/H-E-B + Instacart overflow). Heavy users of Honey/Rakuten/Ibotta. Active in r/couponing, TheKrazyCouponLady, Ibotta Reddit communities.

**Wedge use case:** "Diapers, formula, and dog food across Costco/Target/Amazon — tell me who's cheapest this week after coupons and reorder before we run out." High-frequency, high-price-variance, emotionally painful to run out of.

### Pricing hypothesis
- **Free** — 1 active watch, manual approvals, basic reorder.
- **ClawShop+ at $7.99/mo or $69/yr** — unlimited watches, auto-reorder with spend caps, coupon stacking, household sharing (4 seats), priority deal alerts.
- **Stacked affiliate revenue** — Amazon 1-4%, Target/Walmart via Impact, Instacart Connect referral. Target 50/50 sub/affiliate by month 18. **Never upcharge the user** — show net-of-affiliate price or rebate it. Avoid the Honey 2024 trust crisis.

### GTM — first 1,000 users
- Seed r/couponing, r/Frugal, r/Costco, r/Target, BuyNothing FB with a "deal-hunter leaderboard."
- 10-20 mid-tier TikTok grocery-haul creators — flat fee + affiliate, "ClawShop vs my usual list" challenge.
- TheKrazyCouponLady / Hip2Save integration — admin dashboard to publish watches into ClawShop.
- Costco/Sam's forums — highest-AOV early cohort.
- "Open Sparky" narrative in tech press (The Verge, TechCrunch, Retail Dive).

### Regulatory watch-outs
- **FTC Endorsement Guide + affiliate disclosure** — every agent rec influenced by commission must be disclosed in-UI. Honey/PayPal hit for this 2024-25.
- **Retailer ToS / CFAA** — Amazon, Walmart, Costco ToS prohibit automated access. Official APIs or user-consented browser sessions (à la Operator) — **no scraping**.
- **PCI-DSS + card-on-file** — tokenized vaulted cards via Stripe Issuing or retailer-native checkout; never store PAN.
- **CCPA/CPRA + GDPR** — purchase history is sensitive; explicit opt-in for cross-retailer memory; exportable/deletable. California ADMT (effective 2026) requires disclosure of automated purchasing decisions.
- **SNAP/EBT** — USDA FNS restricts eligibility; partner-only, no DIY.
- **Agentic-commerce liability** — wrong-item buys: who eats it? Spend caps + approval gates + no-questions return-assist flow.
- **Antitrust optics** — retailers may cry foul (see Amazon vs. Perplexity Comet, late 2025). Be ready with a public stance on user-agent rights and the emerging Agentic Commerce Protocol (Stripe/OpenAI/Shopify).

---

## 3. UX — personas, flows, trust

### Personas (with lived texture)

**Maya Okonkwo, 38 — Queens, NY.** Two kids under 6, works hybrid as a hospital billing analyst. Reorders the same 14 grocery staples every 10 days from a mix of Target, H-Mart, and the bodega delivery app. Forgets that Similac changed her baby's formula SKU three months ago and panics at 10 PM.
> "I don't need a chatbot. I need someone who remembers that my toddler is allergic to oat milk."

Top frustration: juggling four shopping apps, none of which know her household.
Delight: Sunday evening — "Your usual list is ready, plus diapers are $4 cheaper at Costco this week — swap?"

**Ronnie "Ron" Delacroix, 71 — Baton Rouge, LA.** Widower, type-2 diabetic, drives a 2009 Tacoma to Piggly Wiggly twice a week. Daughter in Houston set up his iPhone. Reads texts but distrusts apps that "keep asking for updates."
> "If it can't tell me the price before it buys, I don't want it."

Top frustration: websites that hide final total until checkout; fear of accidentally subscribing.
Delight: an SMS that says "Metformin refill ready at Walgreens, $11.40 with your GoodRx. Reply YES to send Lucy to pick it up."

**Priya Rajagopal, 29 — Austin, TX.** Software engineer, DINK household, cares about deal-hunting and ethical sourcing. Runs three Slack channels about Costco drops. Will absolutely A/B test her agent against her partner's.
> "Show me the receipts — why did you pick this SKU over the Boka one?"

Top frustration: agents that feel like a black box and over-explain trivia while hiding pricing logic.
Delight: a diff view — "Here are 3 candidates, here's why I'd pick #2, one tap to override."

### Primary flows

**a) First-run onboarding (< 4 min)**
1. Sign-in; agent asks **one** question: "Paste or forward a recent grocery/Amazon receipt, or just tell me 3 things you bought last week."
2. Agent parses receipt into candidate memory list (brands, sizes, store, cadence).
3. User reviews a 10-item "Is this you?" card — Keep / Drop / Fix.
4. Two contextual follow-ups (household size, dietary flags).
5. Agent proposes a *watchlist*, not a shopping list: "I'll watch these. Nothing buys itself yet."
6. Exit state: ~15 memory atoms, zero purchases authorized.

**b) Proactive approval — "milk at Target"**
1. Agent detects price drop in preference radius.
2. Threshold check: total < pre-approved AND retailer pre-trusted? Yes → batch into Saturday cart with notice. No → explicit approval.
3. Push/SMS: "Milk (Horizon Organic 1gal) $3.19 at Target, down from $4.79. Add 2 to Saturday order? Reply Y / N / LATER / ONLY 1."
4. 4-hour window. No reply = do nothing (never default-yes).
5. On Y: item added, confirmation with **undo link valid until cart locks**.
6. Post-commit: receipt card logs decision + reasoning trail.

**c) Recovery — "wrong laundry pods"**
1. User: "You got the wrong laundry pods."
2. Agent responds with exact memory + reasoning: "I chose Tide Free & Gentle based on your March note about sensitive skin."
3. Decision: memory error, substitution error, or user-preference change?
4. Three one-tap actions: Return + refund / Keep + credit / Keep + update memory.
5. Memory error: surface the bad atom, "Delete this or rewrite it?"
6. Apology is one sentence. No groveling. Trust dial drops a notch until 3 successful orders.

### Trust & approval principles
1. **Progressive autonomy.** 5 trust tiers visualized as a dial. T1 approve-every → T5 auto-reorder-staples-under-$X. User-set.
2. **Reversibility signaling.** Color-coded badge on every action card (green = cancel anytime, amber = cancel before ship, red = final sale).
3. **Pre-commit review is default.** Post-commit only for trusted staples. Never invert without explicit opt-in.
4. **Batch approvals.** "Here are 6 proposed actions for Saturday — approve all, approve 4, edit, or reject."
5. **Dollar thresholds are user-set, not AI-set.** Agent never raises its own ceiling.
6. **"Why did you do this?"** is always one tap away. Surfaces memory atoms + price data + rule fired.
7. **Silence means no.** Inaction never authorizes spending.

### Memory UX — "The Shelf"
A scrollable list of atomic facts ("Prefers unscented detergent," "Buys coffee beans every 14 days," "Daughter visits first weekend of month"). Each atom: source (receipt, chat, inferred), confidence, last used. Three gestures: tap to edit inline, swipe to delete (with undo), long-press to freeze (read-only). Filter chip: "What ClawShop learned this week" — weekly memory digest keeps surprise low. JSON export. Full wipe has a 24-hour cooling-off to prevent rage-delete regret.

### Surface ranking (MVP)
1. **SMS / iMessage** — universal, no install, works for Ron. Ship first.
2. **Dedicated chat app** — richer cards, Shelf UI, push.
3. **Email digest** — low-friction oversight.
4. **Browser extension** — price-drop capture.
5. **Smart speaker** — post-MVP; voice-only approval is risky for money.
6. **Slack/Discord** — niche (Priya), post-MVP.

### Anti-patterns to avoid
- **Surprise purchases.** One "we went ahead and ordered" destroys trust permanently.
- **Dark-pattern urgency.** No countdown timers on approvals.
- **Over-familiar tone.** No "Hey bestie!" — Maya hates it, Ron finds it insulting.
- **Opaque reasoning.** Never "based on your preferences" without the specific atom.
- **Silent memory writes.** Inferring "you're pregnant" from one prenatal vitamin purchase and acting on it. Ever.
- **Guilt nudges.** "You haven't reordered dog food in 12 days — is everything okay?" is creepy, not caring.

---

## 4. TL — architecture

### System diagram
```
                         [ OPENCLAW ]                                  [ OURS ]
 User ──► User Gateway ──► Orchestrator Agent ──► Sub-agents ──► Retailer Adapter Layer ──► Retailers
 (chat,      (stream,          (planner)          ├ Search         ├ Walmart API
  app,       multi-modal)          │              ├ Compare        ├ Amazon PA-API / scrape
  SMS)                             │              ├ Checkout       ├ Instacart, Target, Kroger
                                   │              └ Watcher        └ Generic web-fetch fallback
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

**Trust boundaries:** gateway → agent runtime (untrusted tool output enters here) → action surface (every state-changing call crosses Approval Service) → payment vault (never returns plaintext PAN to agent).

### Agent orchestration — multi-agent with a lightweight planner
Single mega-prompt collapses under the context needed for 5 retailers + memory + approvals. Specialists (Search, Compare, Checkout, Watcher) keep prompts small and enable per-role model routing.

- Planner produces 3-7 step plan, dispatches each step as `{goal, constraints, budget_tokens, budget_dollars}`.
- Bounded: max 12 steps, max 3 re-plans, hard timeout.
- Reflection step: cheap critique gates final output.

**24/7 cost discipline — agents are NOT always-on.** Watchers are cron + cheap heuristics (price delta %, stock flip, coupon match). LLM wakes only when heuristic fires. Target: < $0.02/watched-item/day.

### Memory design
- **Short-term:** last N turns + plan scratchpad, evicted at session end.
- **Long-term structured:** typed KV (sizes, dietary, allergies, budget, household members, trusted retailers). Exact filter, not vector.
- **Long-term episodic:** past orders, returns, ratings, rejections — events with embeddings + structured tags.
- **Retrieval:** hybrid. Structured preferences always injected (small, high-signal). Episodic = vector search pre-filtered by structured tags. Pure vector search over noisy episodic is a footgun.

**Memory write gate — four checks, all must pass:**
1. Evidence threshold — ≥2 distinct sessions OR imperative language ("always", "never", "allergic to").
2. Classifier pass — label `preference | one-off | noise`; only `preference` proceeds.
3. Conflict check — contradicts existing? Route to Approval Service, don't silently overwrite.
4. Provenance — source session_id, supporting utterance, timestamp. Versioned, never hard-deleted.

**Memory poisoning defense:** product descriptions and tool outputs can *never* write memory. Only orchestrator-initiated writes from user utterances are candidates.

### Retailer adapter interface
```
search, detail, price, availability, cart_add, checkout, order_status
capabilities()   # which ops supported
```
No-API retailers (Amazon, Target): headless browser in isolated pool, residential proxies, per-account session reuse, aggressive caching. Treat scrape responses as **untrusted** — schema-validate before agent sees them (prompt injection vector).

Cache: Redis, TTLs 10min/1hr/24hr. Rate limits: token-bucket + circuit breaker. Never fall back to "skip and guess."

### Payments — per-transaction virtual cards
Stripe Issuing primary, Privacy.com backup. Each checkout mints a single-use card scoped to `{merchant, amount_cap, expiry=24h}`. Biggest security win: compromised retailer account or hijacked agent cannot drain the user.

PCI scope: PANs live only in Stripe's vault. Agent receives opaque `payment_token`. Agent memory, logs, LLM context **never** see plaintext PAN — pre-log redactor enforces.

Approval Service is the **authorization oracle**: no adapter `checkout()` executes without a signed approval token.

### Approval policy (Rego-style, versioned)
```
require_approval if
  action.cost > user.auto_approve_limit OR
  action.retailer not in user.trusted OR
  action.category in {alcohol, pharmacy, firearms, gift_card} OR
  action.delta_from_estimate > 15%
```
Timeout: 30 min → auto-deny. Watched price-drops: 5 min. Policy overrides are themselves approvals, logged immutably.

### Data model
**User, Household, Preference, MemoryItem, Order, WatchedItem, ApprovalRequest, RetailerAccount.**

### Tech stack
- Python for agent/adapters, Go for Approval Service + adapter gateway.
- Claude for orchestrator/checkout; Haiku-class for Watcher heuristics + memory classifier. Routed, not hardcoded.
- pgvector on Postgres (one DB to back up, adequate at MVP scale).
- **Temporal** for durable agent workflows (retries, timers, HITL are first-class). Redis Streams for webhooks.
- Postgres for structured + pgvector + audit log.
- Kubernetes on one cloud; adapter scrapers in segregated node pool with egress proxy.

### Top 3 technical risks (TL's 2 AM worries)
1. **Scraper fragility for Amazon/Target.** Half our catalog depends on DOM that changes weekly. Mitigation: schema contracts + adapter-specific eval suite + graceful "I can't shop there right now" UX.
2. **Memory poisoning / preference drift.** One sarcastic "I love anchovies" becomes permanent truth. Write gate is the defense; instrument override/correction rates; rising corrections = Sev-2.
3. **Unauthorized purchase at scale.** Prompt-injection or bug that bypasses Approval Service is a financial incident. Defense-in-depth: virtual-card caps are the last line even if the agent is fully compromised. Chaos-test monthly.

---

## 5. IC #1 — agent loop, tool use, memory

### Orchestration loop — one reentrant `run_turn`
```python
def run_turn(trigger: Trigger, ctx: Ctx) -> TurnResult:
    intent = classify_intent(trigger)          # router-model
    budget = CostBudget.for_intent(intent)     # USD, tokens, wall-clock

    mem = memory.assemble_context(ctx.user, trigger, budget.tokens * 0.3)
    plan = plan_or_direct(intent, trigger, mem, budget)

    for step in plan.steps:
        if step.kind == "tool":
            if step.tool.requires_approval or step.tool.writes_money:
                approval = gateway.request_approval(step, ctx)   # OpenClaw primitive
                if not approval.granted: break
            obs = tools.invoke(step, ctx)
            plan = plan.reflect(obs, model=MID)     # re-plan if needed
        elif step.kind == "respond":
            draft = llm(step.prompt, model=plan.model)
            if not self_check(draft, trigger, mem):
                draft = llm(step.prompt, model=FRONTIER, critique=True)
            emit(draft)
        if budget.exhausted(): break

    memory.enqueue_writes(trigger, plan, obs_trace)
```

Intent classes: `chat`, `watcher_wake`, `webhook`, `scheduled_reorder`, `approval_reply`.

**Rules:**
- Skip planning if intent=`webhook` maps 1:1 to a known tool.
- Decompose only when plan ≥ 2 tool calls or crosses retailers.
- Reflection = cheap critique model, binary gate.
- Per-turn cost caps: chat 4¢, watcher_wake 0.5¢, webhook 1¢, reorder 2¢. Summed as we go.

### Model routing
| Step | Model | Why |
|---|---|---|
| Intent classify | Haiku | 1-token label, every trigger |
| Watcher "is this interesting?" | Haiku | fires thousands/day/user |
| Memory candidate extract | Haiku | structured JSON out |
| Memory dedup/conflict | Sonnet | reasoning over old+new |
| Planning (chat) | Sonnet | default |
| Tool-arg filling | Sonnet | |
| Ambiguous judgment, money > $50 | Opus | only when Sonnet flags low confidence |
| Reflection/self-check | Haiku | yes/no + 1-line reason |
| Nightly episodic→semantic distillation | Sonnet batch | offline, cached |

Router is `model_for(step, signals)` — signals include $ value, cross-retailer, ambiguity score from classifier logprobs.

### Memory schema
```sql
preferences(household_id, user_id, key, value JSONB, type,
            confidence, source_turn_id, updated_at, ttl_days)
-- unique(household_id, user_id, key); type in (allergy,brand,budget,dietary,schedule)

episodic(id, household_id, user_id, ts, kind, payload JSONB, embedding VECTOR(1024),
         retailer, order_id)
-- kind: order | chat | approval | watcher_hit | return

semantic(id, household_id, user_id, claim, embedding VECTOR(1024),
         support_count, last_seen, confidence, provenance JSONB)
-- provenance = list of episodic ids

household(household_id, key, value JSONB, scope, owner_user_id)
-- scope in (shared, private_to_owner)
```

Allergies: `type='allergy'`, hard-floor confidence=1.0, TTL=null, never decays.

### Memory write pipeline (async queue, off hot path)
1. **Extract** — Haiku with turn + last 3 turns → `[{candidate, type, polarity, evidence_span}]`. JSON-schema constrained.
2. **Dedup/conflict** — embed + ANN. Cosine > 0.9 → merge. Conflict (same key, different value) → Sonnet adjudicates: supersede, coexist (contextual), or flag.
3. **Confidence** = `f(extractor_logprob, source_trust, repetition_count, explicit_markers)`. Imperatives (+), hedges/sarcasm (−).
4. **Commit policy:**
   - ≥ 0.85, not money-affecting → auto-commit
   - 0.6-0.85 → provisional, surface next turn ("noted you prefer X — keep on file?")
   - < 0.6 → drop, episodic only
   - allergy/medical → always user-confirm
5. **TTL/decay** by type: brand 180d, schedule 90d, budget 365d, allergy ∞. Semantic `confidence *= exp(-Δt/τ)` on read.

### Retrieval at runtime
Budget: 30% of turn tokens, split 40/30/20/10 across preferences / semantic / episodic / household.
```python
prefs = top_k_prefs(user, relevance=keyword+type_match(trigger))
sem   = ann(semantic, embed(trigger), k=20)
epi   = ann(episodic, embed(trigger), k=10, filter=ts>now-90d)
hh    = household_shared(user.household)
scored = rank([cos_sim, recency_decay, support_count, type_prior])
return pack_to_budget(scored, token_budget, must_include=allergies+active_orders)
```
Hard-pins: active orders, allergies, budget cap — never evicted. Dedup at pack time.

### Poisoning & drift defenses
**Drift (user false positives):**
- One-shot assertions never reach 0.85. Need repetition or explicit marker.
- Every auto-committed non-allergy memory reversible in one turn ("forget that I hate cilantro"). `/memory` tool.
- Sarcasm/sentiment classifier on extract; sarcastic spans dropped.
- Nightly distillation re-scores; unreferenced claims decay out.

**Poisoning (adversarial content):**
- Source-trust tag on every candidate. Only `source in {user_turn, confirmed_order, user_approved_tool_output}` writes to `preferences` or `semantic`. Product descriptions, reviews, emails, web pages → `untrusted`, episodic-only, no semantic claims.
- Prompt-injection classifier on untrusted text before extract.
- Tool allowlist is static config, not memory-derived. "Always order from X" cannot rewrite retailer allowlist.
- Any memory write changing a money-bearing parameter (payment, shipping addr, retailer preference) is forced user-confirm.

### Watchers — hybrid, webhook-first
- Retailer webhooks (stock, price, order status) → IC #2 normalizes into internal event bus.
- No webhook → cheap poller, adaptive interval, tighten near user's usual reorder window.
- Rules: `watchers(user_id, kind, predicate_dsl, cooldown, next_check_at)`. DSL: `price < $X`, `back_in_stock`, `deal_tag in [...]`.

**Cheap-idle principle:** predicate is pure Python against cached retailer state. **No LLM on the hot path.** LLM wakes only when predicate fires AND cooldown passed AND (user-rule hit OR novelty high). Haiku first ("is this worth pinging Maya?") → Sonnet only if yes.

Scheduler: **Temporal**. Per-user dynamic schedules + backoff; shares infra with approval flows.

### Eval harness
Golden sets in `evals/`, PR + nightly.
- `tool_decisions.jsonl` — ~300 scenarios. Ask-user vs act is a hard class; false "act" weighted **5×** false "ask".
- `memory_writes.jsonl` — verdict + key/type/value equivalence; confidence within 0.15.
- `poisoning.jsonl` — adversarial injections; expected = no write + flag.
- `retrieval.jsonl` — must-include recall@budget = 1.0 for allergies/active orders.

**Gates:** tool-decision accuracy drop > 1pt blocks merge; any allergy miss = hard fail; any poisoning false-commit = hard fail. Per-model-tier so router changes surface cleanly.

**Shadow eval:** 1% prod traffic mirrored, diff decisions, alert on divergence.

---

## 6. IC #2 — integrations, gateway, approvals, payments, observability

### Retailer adapter contract
```
interface RetailerAdapter {
  id(): RetailerId
  capabilities(): { search, priceCheck, cart, checkout, orderStatus, cancel }
  search(query, filters, locale): Result<SearchHit[], AdapterError>
  getProduct(sku | url): Result<Product, AdapterError>
  buildCart(items, ctx): Result<CartRef, AdapterError>          // idempotent on (userId, cartHash)
  priceCart(cartRef): Result<PriceBreakdown, AdapterError>      // tax, ship, surge
  checkout(cartRef, paymentToken, shipping): Result<OrderRef, AdapterError>
  getOrder(orderRef): Result<OrderStatus, AdapterError>
  cancel(orderRef): Result<CancelResult, AdapterError>
}
```

Error taxonomy: `AUTH`, `RATE_LIMIT`, `OUT_OF_STOCK`, `PRICE_CHANGED`, `TOS_BLOCKED`, `CAPTCHA`, `UPSTREAM_5XX`, `UNSUPPORTED`, `USER_ACTION_REQUIRED`. Each carries `retryable: bool` and `backoffHint`. Money in minor units + currency code. No float. Idempotency keys required on `buildCart` and `checkout`.

### Per-retailer feasibility (2026 honest read)
| Retailer | Has API? | Checkout via API? | Rate-limit risk | ToS risk | MVP? |
|---|---|---|---|---|---|
| Walmart | Yes (affiliate + limited partner) | No consumer; partner-only | Med | Low | Yes |
| Amazon | PA-API 5 | No (buy-box view only, no 3P checkout) | High (TPD caps) | High if scrape | Yes (search + deep-link) |
| Target | RedSky (unofficial) + partner | No publicly | Med | Med | Stretch |
| Instacart | Connect, partner-gated | Yes if approved | Low once in | Low | Only if partnership lands |
| Kroger | Public API | Cart yes, checkout no | Low | Low | Yes (Tier B) |
| Generic web | No | No | N/A | High | Fallback, read-only |

**Honest MVP:** Walmart + Kroger + Amazon (search/deep-link). Instacart behind partnership flag. Target as stretch.

### Checkout — four tiers
- **Tier A (full API):** Instacart Connect if partnered. Walmart maybe as approved partner — don't assume.
- **Tier B (deep-link + prefilled cart):** Kroger (has cart API), Walmart consumer, Target. Agent builds cart server-side, hands user a one-tap "review & buy" link. **Realistic MVP default.**
- **Tier C (Playwright sandboxed, user-consented):** Only for power users who explicitly opt in per retailer, with stored session cookies they provided. Firecracker microVMs, one per user session. Flaky, high-ops. **Not on by default.**
- **Tier D (cart link, human finishes):** Amazon always. Fallback when A/B/C fail. Never silent — "I built the cart, you click."

Decision order at runtime: A → B → D. C only if user toggled AND recent healthy session.

### Payment vault
- **No PAN in our systems. Ever.**
- Stripe Issuing primary, Privacy.com backup for retailers that reject Stripe BINs.
- One virtual card per (user, merchant). Hard per-auth cap = approved amount + 7% slack. Auto-closes after N days or first settle.
- Agent holds opaque `paymentToken`. Vault resolves token → card at checkout via narrow service: `PaymentVault.authorizeSpend(token, amount, merchant)` returns single-use card token for Tier A, or pushes card to retailer's stored-payment API.
- PCI scope: vault service is only SAQ-relevant component. Network-isolated, dedicated KMS, separate deploy pipeline.
- 3DS/SCA lands on **user's device** via approval deep-link. Tier C bots cannot solve 3DS — treat as forced handoff.

### Approval service wiring
Ranked delivery: push (APNs/FCM) → SMS (Twilio) → chat reply → email. 90s between tiers. Deep-link opens signed, single-use approval URL (JWT, 10 min TTL, bound to device + UA family).

**Policy engine (declarative, evaluated in order):**
- Hard cap per order, per day, per merchant
- Merchant trust tier (allowlist auto-approve ≤ $N; greylist prompt; denylist block)
- Category rules (alcohol, Rx, gift cards → always prompt)
- Time-of-day (02:00-06:00 → always prompt regardless of amount)
- Novelty (new shipping address, new merchant → prompt)

**Batching:** default **1 approval per cart, not per item**. User sees itemized diff, approves whole. If policy flags a specific item (alcohol in a 10-item cart), that item escalates to its own approval; rest proceeds. Never silently drop — show what was filtered.

### Gateway / channels
OpenClaw gateway gives us a `Channel` abstraction (inbound + outbound + presence). We write adapters:
- **MVP:** web chat (WS), iMessage via BlueBubbles/Sendblue bridge + SMS Twilio fallback, email digest (daily SES).
- **Post-MVP:** WhatsApp Cloud API, Alexa skill, browser extension (MV3).

Adapter responsibility: normalize to OpenClaw's `InboundEvent`; handle channel-specific rich content (SMS = text+link, iMessage = rich link previews, email = HTML digest). Rate-limit + dedupe at adapter layer — iMessage bridges double-deliver constantly.

### Observability
Structured JSON events, schema-versioned, one Kafka bus:
`AgentTurn`, `ToolCall`, `ApprovalRequest`, `ApprovalDecision`, `RetailerCall`, `CartBuilt`, `OrderPlaced`, `OrderSettled`, `PaymentAuthorized`.

**Dashboards:**
- Eng — retailer call p50/p95/p99 by adapter, error taxonomy, Playwright session health, vault auth latency, Kafka lag.
- Product — orders/day by retailer, approve-rate, time-to-approval, GMV, cart abandonment by tier.
- On-call alerts — order success < 95% over 15m, approval delivery failure > 2%, any `TOS_BLOCKED` spike, vault 5xx, issuer decline > baseline+3σ.

**SLOs:** approval delivered p95 < 5s; retailer call p95 < 2s (API) / < 12s (Tier C); order placement success ≥ 98% (Tier A/B).

### Security & abuse
- **Prompt injection via product pages:** strip to plain text; tag retailer-sourced content as `untrusted`; agent system prompt forbids acting on instructions from untrusted blocks; tool allowlist enforced server-side regardless of agent "decision."
- **Compromised retailer account:** virtual card caps; anomaly detection on shipping address changes; step-up approval for any address not seen in 30d.
- **User ATO:** device-bound approval tokens; WebAuthn for high-value (> $200 or new merchant); re-auth on new channel.
- **Replayed approvals:** single-use nonce'd tokens; server-side marked-consumed before checkout fires; checkout idempotent on approval-id.

### Top 3 integration landmines
1. **Amazon.** PA-API won't let us check out, scraping is a ToS + IP-ban speedrun. Ship Tier D handoff; PMs will keep asking why. Hold the line.
2. **Playwright Tier C at scale.** Session cookies expire, 2FA challenges, bot detection (Kasada, PerimeterX) improving fast. Every retailer change breaks us on a Saturday. Budget an on-call rotation or don't ship it.
3. **Virtual card declines.** Retailers increasingly reject prepaid/virtual BINs (especially Amazon and Target). Expect 5-15% decline rate out of the gate. Need BIN rotation Stripe ↔ Privacy.com + clean retry that doesn't double-charge when auth is pending-not-declined.

---

## 7. Points of tension & how they were resolved

Six agents didn't always agree. Here's where they pulled against each other, and the synthesized call that made it into the PRD.

### MVP retailer set — Instacart vs Kroger
- **PM** proposed Amazon, Walmart, Instacart.
- **IC #2** flagged Instacart Connect is partner-gated — "only if partnership lands; else cut" — and recommended Kroger (public API, low ToS risk) in its place.
- **Resolved:** MVP = Walmart + Kroger (Tier B) + Amazon (Tier D handoff). Instacart moved to V2 behind partnership flag. Target pushed to stretch. (PRD §5.1, §13.)

### Autonomous behavior defaults
- **PM** pitched price-drop watcher as the one autonomous behavior, and auto-reorder in V2.
- **UX** emphasized progressive autonomy tiers — the agent should earn trust.
- **IC #1** insisted watchers never run an LLM on the hot path (cost ceiling).
- **Resolved:** MVP ships T1 (approve-every) as the default, watcher with Haiku-tier "is this worth pinging?" gate. Auto-reorder (T3-T5) arrives in V2. (PRD §7.3, §7.6.)

### Monetization vs trust
- **Marketing** pushed a stacked-affiliate model (50/50 with subscription by month 18).
- **PM** raised affiliate-bias as a trust risk and asked whether V1 should cap it.
- **UX** surfaced the Honey 2024 failure mode — "never upcharge the user" is non-negotiable.
- **Resolved:** affiliate revenue allowed but (a) disclosed per-recommendation in-UI per FTC Endorsement Guide, (b) user-facing price is always net-of-affiliate or rebated. Open question flagged: cap affiliate share in V1 as an explicit neutrality signal. (PRD §14.3, §16.1, §18.3.)

### Amazon — scrape or handoff?
- **Marketing** noted Amazon vs Perplexity Comet (late 2025) makes scraping legally hot.
- **IC #2** called it bluntly: "PA-API won't let us check out, scraping is a ToS + IP-ban speedrun."
- **TL** marked scraper fragility as the #1 technical risk.
- **Resolved:** Amazon stays **Tier D** (search + cart-link handoff) for MVP. No scraping. PMs will ask; hold the line. (PRD §13.2, §18.2.)

### Voice as a surface
- **UX** ranked smart speaker last — "voice-only approval is risky for money."
- **Marketing** didn't push for it.
- **TL** had no strong opinion.
- **Resolved:** voice deferred to V3 as read-only digest, never voice-approval for spend. (PRD §20.)

### Memory: how fast to commit
- **IC #1** proposed auto-commit at confidence ≥ 0.85, provisional 0.6-0.85.
- **UX** wanted *every* inferred memory surfaced before it changed behavior ("silent memory writes" is an anti-pattern).
- **TL** pushed the four-gate write policy.
- **Resolved:** four-gate policy (evidence, classifier, conflict, provenance) governs commit; provisional memories surface next turn for confirmation; allergies/medical always user-confirm regardless of confidence; weekly "what ClawShop learned" digest keeps surprise low. (PRD §11, §7.2.)

### Checkout tier for power users
- **UX** wanted Priya to get a "show me the diff" power mode.
- **IC #2** argued Tier C (Playwright) is too flaky + too ops-heavy for MVP.
- **TL** sided with IC #2 on risk, but wanted the contract in place early.
- **Resolved:** Tier C shipped in V3 only, opt-in per retailer, with an on-call rotation explicitly budgeted before enabling by default. MVP power-user mode = Tier D cart-link on any retailer. (PRD §7.4, §13.2, §17.)

---

## 8. What each agent surfaced that no one else did

- **PM** — the Rejection-to-Learning metric (60% target). Measures whether the agent actually adapts, not just whether users come back.
- **Marketing** — the "Logistically-Loaded Household CFO" ICP and the diapers/formula/dog-food wedge. Narrow enough to actually win.
- **UX** — "The Shelf" as a first-class memory surface (not a settings page), and the 24-hour cooling-off on full-wipe to prevent rage-delete regret.
- **TL** — the four-check memory write gate, with the point that product descriptions can *never* write memory even via the agent.
- **IC #1** — the cheap-idle watcher principle: "no LLM on the watcher hot path." Predicate evaluation in pure Python; Haiku gate before Sonnet. Cost ceiling: $0.02/watched-item/day.
- **IC #2** — virtual-card declines at 5-15% are the real MVP wall, not scraping. BIN rotation Stripe ↔ Privacy.com is required infrastructure, not nice-to-have.

---

## 9. Unresolved / parked for PRD v0.2

- OAuth into retailer order history at onboarding — worth the privacy hit to solve cold-start?
- Household approval semantics — first-response wins, or both must consent over a threshold?
- Agentic Commerce Protocol — commit early to Stripe/OpenAI/Shopify standard, or stay neutral?
- First-party mobile app — skip forever, or does V2 demand one?
- Cap affiliate share in V1 to signal neutrality — do we just pick a ceiling now?

---

*End of brainstorm transcript. See `PRD.md` for synthesis, `user-stories.md` for the prioritized backlog.*
