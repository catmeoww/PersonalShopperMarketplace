# ClawShop — User Stories

Working name for an OpenClaw-based personal shopper. Stories are grouped by epic and sized for an MVP built by 2 ICs + 1 TL in ~8 weeks. Priority: **P0** = ship-blocker, **P1** = MVP target, **P2** = V2 (90d), **P3** = V3 (180d).

Format: `As a [persona], I want [capability] so that [outcome].` Each story carries acceptance criteria. Personas are defined in `PRD.md` §3.

---

## Epic A — Request intake & intent

**A1 (P0). As Maya, I want to text "we're out of diapers and coffee" and get a ready-to-approve cart, so that I don't have to open five apps.**
- Agent parses free-text into a shopping list of SKU candidates.
- Candidates are matched against known preferences (brand, size, store).
- Agent returns one consolidated proposal with per-item prices, per-retailer splits, and a single approval action.
- Response round-trip ≤ 20s p50 over SMS.

**A2 (P0). As any user, I want to paste a recipe URL and get the cheapest ingredient set across retailers, so that I stop overpaying at one store.**
- Agent extracts ingredient list from common recipe sites.
- Cross-retailer price compare on available retailers (MVP: Walmart, Kroger, Amazon search-only).
- Proposal shows total delivered cost, not just sticker price (tax + shipping included).

**A3 (P1). As Priya, I want to ask "what changed on my watchlist this week?", so that I can act on deals without opening the app.**
- Weekly email digest + on-demand chat summary.
- Each entry: item, price delta, retailer, recommended action, one-tap approve.

**A4 (P1). As Ron, I want to reply in plain SMS with short answers ("Y", "N", "LATER", "ONLY 1"), so that I don't have to learn an app.**
- SMS-first interaction model with no dead-ends into app-only flows.
- All approval actions reachable via SMS deep-link or text reply.

---

## Epic B — Long-term memory & preferences

**B1 (P0). As Maya, I want ClawShop to remember my kids' sizes, my partner's coffee brand, and our weekly cadence, so that I never re-explain them.**
- Preferences (size, brand, dietary, cadence) are stored as typed structured memory keyed by household + user.
- Memory is read into every relevant agent turn with explicit token budget.

**B2 (P0). As a caregiver, I want ClawShop to remember Mom's prescription brand and dosage, so that I never have to re-explain it.**
- Allergy and medical memory is pinned, never decays, and always retrieved.
- Medical memory write requires explicit user confirmation regardless of confidence.

**B3 (P0). As any user, I want to inspect, edit, and delete what the agent remembers, so that I stay in control.**
- "The Shelf" surface shows every memory atom: value, source, confidence, last used.
- Tap-to-edit, swipe-to-delete (with undo), long-press to freeze (read-only).
- JSON export. Full wipe has a 24-hour cooling-off window.

**B4 (P0). As any user, I want the agent to never ossify a sarcastic or one-off comment into a permanent preference.**
- Single-mention, non-imperative statements never auto-commit at high confidence.
- Provisional memory surfaces back to the user next turn ("noted you prefer X — keep that on file?").
- Sentiment/sarcasm classifier runs on every candidate memory.

**B5 (P1). As a subscription-box user, I want ClawShop to learn my rejections ("never Brand X milk"), so that future suggestions improve.**
- Rejections produce a durable `dispreference` memory with polarity.
- Re-proposal of a rejected item requires justification ("price dropped 40%, override?").

**B6 (P1). As a household, I want to share a profile with my spouse, so that either of us can approve and both learn the same preferences.**
- Household scope for memory (shared pantry, shared budget); per-user scope for private items.
- Approvals routed to any household approver; first response wins.

**B7 (P2). As any user, I want a weekly "what ClawShop learned this week" digest, so that surprise is low and trust is high.**

---

## Epic C — Action approval & trust

**C1 (P0). As any user, I want to approve or reject every purchase above a threshold I set, so that I stay in control of spend.**
- User-configurable dollar threshold, per-merchant trust tier, per-category rules.
- No action ever executes without an approval token from the Approval Service.

**C2 (P0). As any user, I want a clear preview (items, totals, tax, shipping, delivery window) before I approve, so that I'm never surprised.**
- Approval card shows itemized cart, reversibility badge per item, total delivered cost, retailer, payment method last-4 only.

**C3 (P0). As any user, I want inaction to mean "no", so that silence never authorizes spending.**
- Approvals time out to `denied`, not `approved`. Default 30 min; 5 min for perishable price-drops.

**C4 (P0). As any user, I want to see why ClawShop proposed each item (memory atoms + price + rule fired), so that I trust the recommendation.**
- "Why?" affordance on every proposal, surfacing supporting memory ids, price signal, and policy rule.

**C5 (P1). As a trusted user, I want batch approval of a weekly cart, so that I don't get 20 pings a week.**
- Default batching: one approval per cart, not per line item.
- Flagged items (alcohol, pharmacy, new merchant) escalate to their own approval.

**C6 (P1). As any user, I want progressive autonomy tiers, so that I can ratchet trust up or down.**
- Five tiers: T1 approve-every-action → T5 auto-reorder-staples-under-$X.
- Trust is user-set, never agent-raised. A misfire drops autonomy one tier with a visible indicator.

**C7 (P1). As any user, I want to undo a recent approval within a short window, so that accidental taps are recoverable.**
- Undo affordance on every confirmation card, valid until cart locks or retailer commits.

---

## Epic D — Retailer execution

**D1 (P0). As Maya, I want ClawShop to check out on Walmart/Kroger via a one-tap link with a prebuilt cart, so that I don't rebuild the list manually.**
- Tier B (deep-link + prefilled cart) is the default MVP checkout path.
- Cart hash is idempotent; duplicate clicks don't double-build.

**D2 (P0). As any user, I want Amazon items surfaced in comparisons even though checkout is hand-off, so that I'm not blind to Amazon pricing.**
- Amazon Tier D (search + cart-link handoff only). Explicit UI label "click to buy on Amazon".
- Never silently skip Amazon — show handoff state clearly.

**D3 (P1). As a home chef, I want out-of-stock items auto-substituted with approved alternatives, so that my cart doesn't fail at checkout.**
- Substitution policy learned from past approvals ("you accepted Brand Y 3 times as substitute").
- Substitutions always surface in the approval card, even for trusted users.

**D4 (P1). As any user, I want a clear failure message when a retailer API breaks, with a manual fallback, so that my week isn't ruined.**
- Error taxonomy: `AUTH`, `RATE_LIMIT`, `OUT_OF_STOCK`, `PRICE_CHANGED`, `TOS_BLOCKED`, `CAPTCHA`, `UNSUPPORTED`.
- Every error maps to a user-facing message + next-step affordance.

**D5 (P1). As Priya, I want a "build cart, hand me the link" mode for any retailer, even ones without deep integration.**
- Tier D fallback available for any supported SKU source.

**D6 (P3). As a power user, I want to opt into browser-automation checkout (Tier C) with my stored session, so that end-to-end checkout works.**
- Opt-in per retailer. Firecracker microVM per session. Session health visible.

---

## Epic E — Payments & security

**E1 (P0). As any user, I want ClawShop to never store my raw card, so that a breach can't drain me.**
- No PAN in our systems. Stripe Issuing (primary) / Privacy.com (backup) virtual cards.
- Agent holds only an opaque `paymentToken`.

**E2 (P0). As any user, I want each virtual card capped per transaction, so that a bug or compromise has blast-radius limits.**
- One virtual card per (user, merchant) with hard cap = approved amount + 7% slack.
- Card auto-closes after N days or first settle.

**E3 (P1). As any user, I want step-up authentication (device-bound, WebAuthn) for high-value or new-merchant approvals, so that takeover is hard.**
- WebAuthn on approvals > $200 or new merchant not seen in 30 days.
- Single-use, device-bound approval JWTs, 10 min TTL.

---

## Epic F — 24/7 watchers & autonomous actions

**F1 (P0). As Maya, I want a watchlist that pings me on price drops ≥ 15%, so that I buy at the right moment.**
- User-configurable price predicate per watched SKU.
- Cooldown per watcher to prevent notification spam.

**F2 (P1). As a caregiver, I want auto-reorder of staples with a monthly spend cap, so that I don't have to remember.**
- Cadence-driven proposals, always approval-gated in MVP.
- Monthly cap enforced at the approval layer, not agent-discretion.

**F3 (P1). As a deal hunter, I want a back-in-stock alert with one-tap approve-and-buy, so that I beat the restock crowd.**
- Webhook-first, polling fallback with adaptive interval.

**F4 (P2). As a trusted user at T4-T5, I want staples under $X to auto-reorder without a synchronous approval, so that the agent feels actually autonomous.**
- Post-commit notification with a reversal window.

**F5 (P0). As an ops owner, I want the watcher to NOT run an LLM on every tick, so that 24/7 doesn't bankrupt us.**
- Predicate DSL evaluates in pure Python against cached state.
- LLM wakes only when a predicate fires AND cooldown passed AND a Haiku-tier "is this worth pinging?" gate passes.

---

## Epic G — Recovery & correction

**G1 (P0). As any user, I want to tell ClawShop it got something wrong and choose return/keep/update-memory in one tap, so that recovery is not a 6-step slog.**
- Chat command + app card both support: **Return + refund**, **Keep + credit**, **Keep + update memory**.
- If the error is a bad memory atom, surface the atom with delete / rewrite options.

**G2 (P0). As any user, I want ClawShop to pause and ask when unsure, so that I don't get the wrong thing silently.**
- Agent self-check step before committing. On low confidence, escalate to ask-user.
- Ask-user vs act is a hard classification boundary in the eval harness; false "act" is weighted 5× false "ask".

**G3 (P1). As any user, I want the agent to apologize once, update its memory, and move on — not grovel.**
- Post-error UX drops autonomy one tier, shows a single-line apology, and records a correction event.

---

## Epic H — Observability, evals, safety (user-adjacent)

**H1 (P0). As a user, I want my preferences and order history exportable and deletable on request, so that I am not locked in.**
- JSON export of memory + orders. Full-delete with cooling-off.
- CCPA/CPRA + GDPR compliant.

**H2 (P0). As a user, I want every affiliate-influenced recommendation disclosed in-UI, so that I trust ClawShop is on my side.**
- FTC Endorsement Guide compliant. Per-recommendation disclosure badge.
- We never upcharge the user for affiliate revenue.

**H3 (P1). As an internal operator, I want golden-set evals to block deploys on regressions, so that we never ship a worse agent.**
- Covered by `evals/` suite: tool-decisions, memory-writes, poisoning, retrieval.
- Allergy-retrieval miss = hard fail. Poisoning false-commit = hard fail.

---

## Out-of-scope for MVP (explicitly)

- Native full-API checkout on retailers that don't expose it (Amazon, Walmart consumer).
- Browser-automation Tier C checkout as a default.
- Mobile native app (web chat + SMS + email cover the MVP).
- Voice (Alexa/Google) — approval UX too risky for money in voice-only.
- Recipe generation, meal planning, nutrition scoring.
- Reseller/pro-buyer tooling, bulk ordering, tax handling.
- EBT/SNAP routing (regulatory, partner-only).
- Local grocers beyond Kroger.
- Returns orchestration beyond the 3-button recovery flow.
