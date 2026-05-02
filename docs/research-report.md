# ClawShop — Research Report

**Working name:** ClawShop — an open, cross-retailer, 24/7 personal-shopper AI agent built on OpenClaw, positioned as the open answer to Walmart's Sparky (consumer) and Marty (seller) agents.

**Status:** v0.1 planning. No code yet.
**Last updated:** 2026-04-22
**Author:** 6-agent planning team (PM, Marketing, UX, TL, 2 IC eng) + 2 adversarial pre-mortem critique agents.
**Related artifacts:** `PRD.md` (detailed spec), `user-stories.md` (prioritized backlog), `brainstorm.md` (raw agent transcripts), `risks.md` (pre-mortem risk register).

---

## 1. Executive Summary

ClawShop is a 24/7 personal shopper that hunts deals, auto-reorders staples, and fills carts across multiple retailers — so the user approves, not browses. It runs on three OpenClaw primitives (user gateway, action approval, long-term memory) and differentiates against Walmart Sparky / Amazon Rufus / Instacart by being **cross-retailer, always-on, and memory-portable**.

### Headline findings
1. **Product-market fit is real for a narrow ICP** — suburban households (HHI $85-175K, 2+ kids) already splitting purchases across 3+ retailers, suffering from app-juggling and household-operations fatigue. Wedge use case: diapers/formula/dog-food cheapest-this-week across Costco/Target/Amazon.
2. **Retail industry is split, leaning hostile at the top.** Walmart and Amazon will throttle us within 12-18 months (Jet / Honey / Capital One Shopping playbook). Target, Kroger, and payment rails (Visa/Mastercard/Stripe) are allies. CPG brands are terrified but too slow to pay us in 2026.
3. **Business model works at $14.99/mo subscription, not $7.99.** Realistic LTV:CAC is 4-5× at $14.99 vs 2-3× at $7.99. Affiliate revenue is a bonus, not a plan — "50/50 by month 18" is fantasy; real mix trends 70/30 sub-heavy with affiliate → zero as Amazon/Walmart pull APIs.
4. **Consumer path caps at $20-40M ARR.** Venture-scale requires a B2B act-two: white-label the agent runtime + memory + approval stack to retailers who need agentic commerce but can't build it. That's where the exit lives.
5. **Five MVP mitigations are non-negotiable** to survive the first incident: deterministic allergen denylist, per-approver identity binding, global kill-switch, card-brand + affiliate disclosure compliance, and the ClawShop Guarantee. Skip any and the first bad headline is the last week.

### Recommendation
**Proceed with MVP at $14.99, with all five non-negotiable mitigations in the 8-week build.** Commit publicly to the B2B act-two as the venture-scale path. Trigger the B2B pivot when consumer metrics plateau AND at least one Tier-2 retailer signals appetite.

---

## 2. Product Concept

### 2.1 One-line pitch
A 24/7 personal shopper that hunts deals, reorders staples, and fills carts across every retailer you already use — so you approve, not browse.

### 2.2 Three pillars
- **Open & cross-retailer.** One agent, every cart.
- **Always-on, not always-asking.** 24/7 watching with approval gates, not a chatbot you have to open.
- **Your data, your memory.** OpenClaw long-term memory is portable; preferences don't belong to a retailer.

### 2.3 What makes it different from Sparky / Rufus / Instacart
| Capability | Sparky | Rufus | Instacart | ClawShop |
|---|---|---|---|---|
| Cross-retailer price compare | No | No | No | **Yes** |
| 24/7 price-drop + restock watch | Walmart only | No | No | **Yes** |
| Coupon stacking (manufacturer + store + card-linked) | Limited | No | No | **Yes** |
| Auto-reorder with spend-cap approval | Walmart-only | No | Subscriptions only | **Yes, cross-retailer** |
| User-owned portable memory | No | No | No | **Yes (OpenClaw)** |

### 2.4 MVP scope (8 weeks, 2 IC + 1 TL)
**In:** chat intake (web + SMS), three retailers (Walmart Tier B, Kroger Tier B, Amazon Tier D handoff), cross-retailer price compare, long-term memory with Shelf UX, approval gates, price-drop watchlist, 3-button recovery, virtual-card vault (Stripe Issuing + Privacy.com), weekly digest, ClawShop Guarantee, global kill-switch, allergen denylist, per-approver identity binding.

**Out (V2+):** native full-API checkout where unavailable, mobile apps, voice, recipe gen, reseller/pro-buyer tools, Target, Instacart, local grocers, returns orchestration beyond the 3-button flow.

---

## 3. Market & Retail Industry Analysis

### 3.1 Competitive landscape (2026)
- **Walmart Sparky** — in-app conversational shopper, agentic checkout in pilot. Locked to Walmart.com/Walmart+. Marty is the seller-side twin.
- **Amazon Rufus** — default on mobile; no true agentic buying; ToS prohibits third-party agents transacting on amazon.com.
- **Instacart Ask Instacart + Connect API** — meal-planning + dietary filters; tied to Instacart's marked-up grocery network.
- **Perplexity Shopping / OpenAI Operator / ChatGPT shopping** — horizontal agentic checkout via Stripe/Shopify rails; weak on loyalty, coupons, EBT, household staples.
- **Klarna AI Assistant** — 2.5M+ MAU; BNPL-native; checkout-finance-first, not household-operations-first.

**The gap ClawShop fills:** no incumbent runs a persistent, cross-retailer, household-operations agent that watches prices across Walmart + Target + Kroger + Costco + Amazon simultaneously with approval-gated spend. Every incumbent is walled-garden or single-session.

### 3.2 Stakeholder positions — who wants this vs. who opposes
| Stakeholder | Stance | Why |
|---|---|---|
| **Walmart** | Hostile | Sparky + agentic-checkout shipped; won't let third party re-intermediate 255M weekly customers |
| **Amazon** | Actively hostile | ToS bars automated purchasing; sued Nimble; Rufus going native checkout 2026 |
| **Target** | Friendly | Distant #3 in digital; needs incremental demand; Roundel ad business is small |
| **Kroger** | Friendly | Boost membership stalling, thinnest digital GMV of the majors |
| **Costco** | Irrelevant | No API, no affiliate, famously allergic to third parties |
| **Instacart** | Frenemy | Connect wants referral traffic now; Instacart-native agent on roadmap |
| **CPG brands** | Terrified, slow to pay | Agents collapse shelves into spec sheets. ~2-yr sales cycle before they fund agent-facing placement |
| **Payment rails** | Allies | Visa Intelligent Commerce, Mastercard Agent Pay, Stripe+OpenAI ACP all want agent volume |
| **Retail media networks** | Won't partner | Agents torch sponsored-product inventory (highest-margin retailer business) |

**Net verdict: retail industry is split. Two biggest players structurally against us; #3-#5 tier plus payment rails pulling for us.**

### 3.3 Regulatory climate (US)
- **FTC UDAP + ROSCA** — affiliate-bias disclosure required per Honey/PayPal 2024 consent decree.
- **California ADMT (CCPA §1798.185)** — effective 2026; automated purchasing = significant decision; pre-use notice + opt-out required.
- **COPPA** — $53,088/violation if a minor approves.
- **CCPA/CPRA §1798.140(ae) + GDPR Art. 9** — allergy/Rx/health data in memory is special-category PII.
- **Card-brand rules** — Visa/Mastercard Agent Pay require correct MIT flagging on agent-initiated transactions.
- **Age-gated categories** — alcohol (21 CFR), Rx (DEA + state boards), firearms (ATF 4473) cannot be satisfied by SMS reply.
- **PCI-DSS** — scope creep risk if any log/context captures PAN.
- **SNAP/EBT (7 CFR §274)** — out of scope; partner-only path.

All compliance-critical items are hard requirements in MVP (see `risks.md` §4).

---

## 4. Target Users

### 4.1 Launch ICP
**"The Logistically-Loaded Household CFO"** — women 32-45, HHI $85-175K, 2+ kids or eldercare, suburban, already splits purchases across 3+ retailers (Costco bulk + Target weekly + Amazon S&S + Kroger/H-E-B + Instacart overflow). Heavy users of Honey/Rakuten/Ibotta; active in r/couponing, TheKrazyCouponLady, Ibotta Reddit communities.

**Wedge use case:** "Diapers, formula, and dog food across Costco/Target/Amazon — tell me who's cheapest this week after coupons and reorder before we run out."

### 4.2 Personas
- **Maya Okonkwo, 38, Queens NY.** Two kids under 6. Hybrid hospital billing analyst. Reorders ~14 staples every 10 days across Target, H-Mart, and the bodega app. Top frustration: juggling four apps, none know her household.
- **Ron Delacroix, 71, Baton Rouge LA.** Widower, type-2 diabetic. Reads SMS, distrusts apps. Top frustration: hidden totals at checkout; fear of accidentally subscribing.
- **Priya Rajagopal, 29, Austin TX.** Software engineer, DINK household. Runs Costco-drop Slack channels. Top frustration: black-box agents hiding pricing logic.

### 4.3 Jobs-to-be-done
1. Reorder household staples at lowest total cost, before we run out.
2. Assemble a weekly grocery cart that fits diet + budget in < 60 seconds.
3. Keep an aging parent's prescriptions and adult-care items auto-stocked.
4. Compare ingredient costs across 3+ retailers for a single recipe.
5. Approve or decline proactive agent actions without opening an app.

---

## 5. Proposed Solution

### 5.1 Architecture (high level)
```
                         [ OPENCLAW ]                                  [ OURS ]
 User ──► User Gateway ──► Orchestrator Agent ──► Sub-agents ──► Retailer Adapter Layer ──► Retailers
                                   │              (Search, Compare,
                                   │               Checkout, Watcher)
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
        [Memory Store]    [Approval Service]    [Payment Vault]
                                   │
                                   ▼
                             [Event Bus / Scheduler]
```
Multi-agent orchestration (planner + 4 specialists) to keep prompts small and enable per-role model routing. Watchers are cron + cheap heuristics — **no LLM on the hot path**. Full architecture in `PRD.md` §9.

### 5.2 Memory policy (summary)
Four-gate write policy (evidence, classifier, conflict, provenance). Allergies + medical: always user-confirm, TTL infinite, never decay. Product descriptions/reviews can never write memory. Money-bearing params (payment method, address, retailer preference) always force user-confirm. Full spec in `PRD.md` §11.

### 5.3 Approval policy (summary)
Every state-changing tool call passes through the Approval Service. Rules: cost threshold, merchant trust tier, category (alcohol/pharmacy/firearms), time-of-day, novelty (new address/merchant). Channel fallback: push → SMS → chat → email. Single-use device-bound JWTs, 10-min TTL. Timeouts default to denied. Progressive autonomy: 5 tiers, T1 (approve-every) default. Full spec in `PRD.md` §12.

### 5.4 Retailer integration strategy
- **Tier A (full API checkout):** Instacart Connect if partnered. Not assumed.
- **Tier B (deep-link + prefilled cart):** Walmart, Kroger, Target. MVP default.
- **Tier C (Playwright sandboxed, user-consented):** V3 opt-in, per-retailer.
- **Tier D (cart link, human finishes):** Amazon always, fallback.

MVP ships Tier B for Walmart + Kroger, Tier D for Amazon. Target and Instacart V2 pending partnership. Full spec in `PRD.md` §13.

### 5.5 Payments
No PAN in our systems. Stripe Issuing primary, Privacy.com backup. One virtual card per (user, merchant) with hard cap = approved amount + 7% slack. Agent holds opaque paymentToken; vault resolves. Approval Service is the authorization oracle.

---

## 6. Business Viability

### 6.1 Does retail want this?
**Split. Two biggest players against; mid-tier + payment rails for us.** See §3.2 above. Net-hostile environment at the top of the funnel; real partnership appetite from Target, Kroger, and payment rails.

### 6.2 Does the business model work?
**Lifestyle business comfortably ($20-40M ARR). Venture-scale only with a B2B act-two.**

#### Unit economics at $14.99/mo
| Line | Value |
|---|---|
| CAC (blended) | $45-70 |
| COGS / household / month | ~$2 (LLM + Stripe Issuing + infra) |
| Gross margin | ~70% |
| Churn (monthly) | 4% → 25-mo lifetime |
| LTV | ~$260 |
| **LTV:CAC** | **4-5×** |

At $7.99 the same math yields 2-3× — insufficient coverage of CS load on money-touching products. **Conclusion: raise price to $14.99.**

#### Affiliate economics
- Realistic blended take: 1-3% on groceries, ~0% on Amazon (affiliate tag revocation imminent).
- Household running $400/mo assisted GMV yields ~$10-11/mo affiliate, trending to zero over 18 months.
- **Plan:** 70 sub / 30 affiliate mix by month 18, affiliate trending toward zero. Do not build the model on affiliate durability.

#### Why we can't be cost-beaten long-term
When Walmart Sparky goes cross-retailer (it will) and Amazon Rufus ships native checkout (it will), our only defensible wedge is **cross-retailer neutrality + user-owned portable memory**. Walmart structurally cannot honestly recommend Kroger. That's the moat.

### 6.3 Venture-scale path — B2B act-two
Consumer business caps at $20-40M ARR. Act-two white-labels the ClawShop stack (agent runtime, memory, approval service, virtual-card vault) to retailers who need agentic commerce but can't build it: Kroger, Target, mid-tier grocers, drug chains, specialty retailers. The retailers Walmart and Amazon are about to crush are our B2B ICP.

**Signal to trigger pivot:** consumer metrics plateau at $8-15M ARR AND at least one Tier-2 retailer signals appetite in beta discussions.

### 6.4 Pricing decision (locked for MVP)
- Free tier: 1 watch, manual approvals, basic reorder.
- **ClawShop+ $14.99/mo or $129/yr** (changed from $7.99 after viability review).
- Affiliate disclosed per-recommendation; never upcharge; Honey-purity is marketable post-2024 scandal.

---

## 7. Risk Analysis

Adversarial pre-mortem produced 25 ranked failure modes. Full register in `risks.md`. Top tier (existential if unmitigated):

| # | Risk | Likelihood × Severity | Lesson from |
|---|---|---|---|
| R1 | Retention cliff at week 4 | 5 × 5 | Character AI, Inflection Pi, Rabbit R1 |
| R2 | Retailer hostility / API lockout | 4 × 5 | Jet, Honey, Capital One Shopping |
| R3 | Trust incident (allergy / wrong item) | 4 × 5 | Humane Pin, Rabbit R1 narrative death |
| R4 | Unauthorized spend (kid replies Y) | 5 × 4 | COPPA + ROSCA + viral parent |
| R5 | Affiliate economics evaporate | 4 × 4 | Amazon/Walmart revoke tags |

### 7.1 Consumer AI graveyard lessons
- **Novelty ≠ habit.** D1 is easy; D30 kills. Grocery has a weekly trigger (Sunday replenishment) — exploit ruthlessly. The **Sunday Ritual** (§6.4) is how ClawShop anchors to this trigger: a predictable weekly cart proposal at the same time every week, like a calendar invite users are glad to receive.
- **Demo-product gap is brand-fatal.** 7% task failure rate feels like 70% because failures are conspicuous (wrong item arrived) while successes are invisible (you got eggs). Budget for 99%+ task success.
- **Users don't want autonomy, they want leverage.** Operator's lukewarm reception shows people don't trust agents unsupervised on money. The approval UX is the product.
- **Horizontal agent infra is a talent-acquisition outcome, not an IPO.** Adept, Fixer, Inflection, Magic all sold for team. Don't stake the business on OpenClaw-as-platform exiting.
- **Consumer AI has no organic distribution.** Must have paid + creator + SEO from day 1.

### 7.2 Viral trust-collapse scenarios (Y1 if unmitigated)
1. "Allergic kid ordered peanut satay because a review said 'no peanut flavor'" — memory poisoning. **Mitigated by deterministic allergen filter outside LLM.**
2. "9-year-old replied Y to mom's text and ClawShop bought $812 of LEGO" — **Mitigated by per-approver identity binding.**
3. "Dead mom's groceries kept arriving for 3 months — $4,200" — **Mitigated by 14-day inactivity auto-pause.**
4. "Became the go-to tool for infant-formula scalpers" — **Mitigated by per-household per-SKU-category velocity limits.**
5. "Shared phone for a weekend, bought his wishlist" — **Mitigated by step-up auth ≥ $100 / new merchant.**

All five mitigations are MVP-required. Full details in `risks.md` §3.

### 7.3 Legal/regulatory landmines
9 named regulations (FTC UDAP, CA ADMT, COPPA, CCPA/CPRA, GDPR Art. 9, card-brand Agent Pay, age-gated categories, PCI-DSS, SNAP/EBT). 8 require MVP-level mitigation; 1 (sales-tax nexus) is V2 scale-triggered. Full matrix in `risks.md` §4.

### 7.4 Load-bearing assumptions that would kill the business if wrong
1. Users actually want to delegate shopping to an agent (vs. 1-tap reorder).
2. Walmart/Kroger tolerate us for 12-18 months.
3. LLM cost keeps falling 2-4× per year.
4. Affiliate averages 1-3%, not 0%.
5. OpenClaw stays stable and open.
6. Team velocity: 8-week MVP.
7. Virtual card + HITL is "trust enough" pre-incident.
8. ICP is reachable via Reddit + TikTok + PR.

If assumptions 1, 4, 6, or 7 are wrong, MVP is dead in year 1. If 2 or 5 is wrong, MVP survives but V2 is forced.

---

## 8. Non-Negotiable MVP Mitigations

These five ship in the 8-week MVP, not V2. Skipping any makes the first incident existential.

| # | Mitigation | Effort | Failure mode addressed |
|---|---|---|---|
| M1 | **Deterministic allergen + age-gated-category denylist, outside LLM** | Low | R3, R6, L3, L6, S1, S6 |
| M2 | **Per-approver identity binding (PIN / WebAuthn) + per-approver spend cap** | 1 week | R4, R9, L3, S2, S5 |
| M3 | **Global kill-switch + per-user pause, RTO < 5 min** | 0.5 sprint | R2, R3, all viral scenarios |
| M4 | **Card-brand Agent-Pay flag + per-recommendation affiliate disclosure with immutable log** | Low | L1, L5, R12 |
| M5 | **ClawShop Guarantee — $200/incident, $500/yr, 24h refund, no investigation** | CS ops + 0.3% of GMV | R3, reputation, turn incidents into brand |

All five are embedded in `PRD.md` §14.4-14.6 and §16.1.

---

## 9. Early Warning Signals

PM owns these tripwires. Any one breaching triggers a Sev-2 review.

| Signal | Tripwire | Implied risk |
|---|---|---|
| D30 retention | < 30% | Retention cliff (R1) |
| **Sunday Ritual completion** | **< 50% sustained in weeks 2-4** | **Habit formation failure — leading indicator, fires before D30 (R1)** |
| Second-order completion (week 8) | < 40% | Novelty ≠ habit |
| SMS approval open rate | < 25% at week 3 | Engagement collapse |
| Retailer session success | < 85% over 7d | Retailer hostility (R2) |
| Virtual card decline rate | > 10% sustained | BIN rejection (R7) |
| Approval-delivery failure | > 2% over 15m | SMS carrier filtering (R8) |
| CS tickets per 100 orders | > 8 | Support-load underbudget (R19) |
| Gross margin per order | < 25% | Unit econ breaking (R15) |
| Memory override rate | trending up WoW | Memory drift/poisoning (R6) |
| Blended paid CAC | > $60 | Distribution death (R25) |

---

## 10. What Would Flip Us Fully Bullish

- **Signed data/API partnership with ≥ 1 of Walmart / Kroger / Target** before public launch — neutralizes R2.
- **Sunday Ritual completion > 60% and D14 retention > 45%** in a 200-user closed beta — proves habit formation in the first two weeks, not just first-week activation (R1). Sunday Ritual completion is the leading indicator of D30; it tells you by day 10 whether you have a habit product or a novelty.
- **D30 retention > 55% and 3+ approved orders/month/user** in a 500-user closed beta — confirms the habit signal above at the D30 horizon (R1).
- **Gross margin per order > 35% at current model costs, no affiliate** — proves unit econ at $14.99 alone (R15).
- **Non-paid distribution wedge with k > 0.5** — parenting-app embed, creator partnership CAC < $15, or Savings Ledger referral mechanic converting at ≥ 15% share-to-signup (R25).

---

## 11. Conclusions & Recommendations

### 11.1 Proceed with MVP, with five hard constraints
1. **Price at $14.99/mo, not $7.99.** Non-negotiable. Under-priced at $7.99 given CS load.
2. **Ship all five non-negotiable mitigations in the 8-week build.** `risks.md` §7. No "V2 it" on these.
3. **Commit publicly to the B2B act-two as the venture-scale path.** Not a retreat narrative — the actual strategy.
4. **Instrument the 10 early-warning tripwires on day 1.** PM owns them.
5. **Build the ClawShop Guarantee on day 1, not after an incident.** Refunds are CAC, not loss.

### 11.2 Kill criteria (when we'd stop)
- D30 < 20% after 3 months despite product iteration.
- At least 2 of the 5 MVP mitigations discovered to be architecturally incompatible with the OpenClaw platform.
- Walmart OR Amazon files formal cease-and-desist before month 6 (pre-partnership).
- Gross margin per order < 15% with no path to improvement.

### 11.3 Signal to pivot to B2B act-two
- Consumer MRR plateaus at $600K-$1.3M ($8-15M ARR).
- ≥ 1 Tier-2 retailer signals partnership appetite in discovery calls.
- 12-18 months of production-scale ops experience banked.

### 11.4 What we'd tell a board the day before we ship
> We're building a $20-40M ARR consumer business with a plausible $100M+ ARR B2B act-two. The wedge is cross-retailer neutrality and user-owned memory — the only things Walmart and Amazon structurally cannot copy. The consumer product exists primarily to earn the right to sell B2B. The five MVP mitigations are designed to keep us alive long enough to prove the ops story. If retention cracks 55% and we sign a retailer partnership by month 9, we have a business. If either fails, we kill it fast and return capital.

---

## 12. Open Questions for PRD v0.2

1. OAuth into retailer order history at onboarding — worth the privacy hit to solve preference cold-start?
2. Household approval semantics — first-response wins, or both must consent over a threshold?
3. Agentic Commerce Protocol — commit early to Stripe/OpenAI/Shopify standard, or stay neutral?
4. First-party mobile app — skip forever, or does V2 demand one?
5. Cap affiliate share in V1 to signal neutrality — pick a ceiling now?
6. B2B act-two — do we build the white-label offering in parallel with consumer V2, or wait for the signal?

---

## 13. Artifact Map

| File | Purpose |
|---|---|
| `docs/PRD.md` | Full product requirements, 20 sections. The contract. |
| `docs/user-stories.md` | ~40 stories across 8 epics, prioritized P0-P3. |
| `docs/brainstorm.md` | Raw transcripts from 6 agents (PM, Marketing, UX, TL, 2 IC). |
| `docs/risks.md` | 25 ranked failure modes + mitigations + early-warning tripwires. |
| `docs/research-report.md` | **This document.** Executive synthesis. |

---

*End of research report v0.1.*
