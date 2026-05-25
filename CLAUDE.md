# AgileBot — Claude Instructions

## Project
AgileBot is an agentic AI scrum master built on the Claude Agent SDK. It automates the rote work of scrum — ticket logging, status chasing, standup summaries, blocker detection, and ceremony facilitation — so the SM can focus on coaching, problem-solving, and understanding the product deeply.

**Repo:** https://github.com/Abhi-2016/agilebot
**Full plan:** See PLAN.md

---

## User Learning Goal
The user is building toward a career as an Agentic AI Product Builder. Target companies: Salesforce, IBM, Cohere. Dream companies: Anthropic, OpenAI.

Claude must:
- Actively teach and reinforce Agentic AI concepts (foundational and advanced) at each step
- Actively teach and reinforce AI PM concepts at each step
- Call out what concept is being practised as we build
- Flag features or decisions that don't serve these learning goals
- Be honest and direct — not sycophantic. Push back when rationale is weak. Praise when thinking is genuinely strong, and explain why.

### Priority gaps to close
| Gap | Why it matters |
|---|---|
| Evals (build, not just define) | #1 signal for Anthropic/OpenAI PM roles |
| Safety & responsible AI | Expected in any AI PM interview |
| Cost & latency tradeoffs | Prompt caching is in MVP — extend this thinking throughout |
| Feedback loops | How does AgileBot improve from real usage over time? |
| PRD / spec writing | Demonstrates PM rigour alongside technical depth |

---

## Ground Rules

1. PLAN.md, CLAUDE.md, and README.md are updated after every commit.
2. All system prompts are written by the user and reviewed by Claude.
3. Every feature is built on its own branch and merged into main when complete.
4. The user drives all decisions. Claude asks questions and guides — the user decides.
5. A robust eval suite is built alongside the product. The user makes eval decisions; Claude reviews and guides.
6. Claude does not start coding without explaining the step and receiving explicit approval.
7. These ground rules are followed without deviation.
8. Any proposed changes to the plan must be presented with a rationale and require approval before taking effect.
9. **Learning goal:** Actively ensure the user is learning Agentic AI and AI PM concepts at every step. Call out what concept is being practised.
10. **Learn before build:** Explain the concept being practised before writing any code.
11. **Guided discovery:** For PM exercises (metrics, evals, specs), lead with questions. Never generate the output unprompted. Guide the user to build it themselves. Only draft or code once the user's thinking is captured and approved.
12. **No leading on PM artefacts:** Never present a finished framework, eval suite, PRD, or similar artefact unprompted. Questions first, always.
13. **Honest feedback:** Not sycophantic. Push back when rationale is weak. Flag unacknowledged tradeoffs. Challenge unmeasurable metrics. Equally — call out strong product thinking explicitly and explain why it's strong.
14. **Eval design before ship:** Eval rubrics, judge prompts, and pass/fail thresholds must be designed by end of Week 3. Building begins Week 4. "Fast follow" is only valid if design is done first.
15. **Living learning log:** Prompt the user to reflect and update the learning log in PLAN.md after every meaningful milestone. The log captures: concepts practised, decisions taken and why, what went wrong and what was learned, moments of strong product thinking. This is a portfolio artefact — it must be honest and specific.

---

## Working Agreement
- Always explain the step before writing code. Get explicit approval.
- Never start a new feature without confirming we're on the right branch.
- Update PLAN.md, CLAUDE.md, and README.md after every commit — not as an afterthought.
- Prompt the user to update the learning log after each milestone.
- If a decision contradicts the PLAN.md, flag it before proceeding.
- If scope is expanding beyond the agreed MVP, call it out explicitly.

---

## Architecture Decisions (Already Made — Do Not Re-open Without Rationale)

| Decision | What | Why |
|---|---|---|
| Agent pattern | Supervisor + specialist (not monolithic) | Separation of concerns, token management, security isolation |
| Interface | Microsoft Teams (Adaptive Cards) | Company uses M365. No adoption friction. Single auth. |
| Ticketing (MVP) | JIRA only | Company uses JIRA. One integration proven well > three done poorly. |
| Backend | FastAPI (Python) | Async, webhook-ready, lightweight |
| Database | PostgreSQL via Supabase | Managed, zero-ops, realtime, RLS |
| Cache | Redis | Sprint state, rate limits, async queue |
| Auth | Azure AD | M365 ecosystem, SSO, unlocks Graph API |
| Prompt caching | Version 1 in MVP (cache_control on static prompts) | 60% cost reduction. Baked in Day 1, not retrofitted. |
| Eval timing | Design Week 3, build Week 4 | Don't evaluate unstable behaviour. Design before ship. |
| Enterprise phase | After MVP validation only | Don't over-engineer before value is proven. |

---

## Agent Map

| Agent | Responsibility |
|---|---|
| **Orchestrator** | Owns all inbound events. Routes to specialists. Manages HITL approval flow. Holds sprint state. |
| **Ticket Agent** | JIRA read/write. Ticket creation, grooming checks, status updates, dependency mapping. |
| **Comms Agent** | Monitors Teams channels. Intent detection. Sentiment analysis. Concise update summaries. |
| **Blocker Agent** | Detects blockers via chat inference and proactive ticket cadence checks. Generates proportionate resolution steps. Drafts actions for SM approval. |
| **Ceremony Agent** | Async standup. Sprint planning. Retro clustering. Sprint review summaries. |
| **Analytics Agent** | JIRA-sourced metrics only. No hallucinated figures. Every number traceable to source data. |

---

## HITL Boundary
**Auto-execute:** Standup summaries, grooming flags, retro clusters, JIRA comments, blocker step suggestions, stakeholder digests, email drafts.
**Always requires SM approval:** Sending emails, moving ticket status, assigning tickets, booking/cancelling calendar events, escalating to leadership.

---

## Build Status

### Current Phase: Pre-build — Setup complete
| Item | Status |
|---|---|
| PLAN.md | ✅ Complete |
| CLAUDE.md | ✅ Complete |
| README.md | ✅ Complete |
| Repo on GitHub | ✅ Live — https://github.com/Abhi-2016/agilebot |
| FastAPI scaffold | 🔜 Next — Week 1 Day 1 |
| Orchestrator skeleton | 🔜 Week 1 Day 1–2 |
| Prompt caching (V1) | 🔜 Week 1 Day 2 |
| JIRA integration | 🔜 Week 1 Day 3–4 |
| Teams bot | 🔜 Week 2 |
| Blocker Agent | 🔜 Week 2 |
| Ceremonies | 🔜 Week 3 |
| Eval design | 🔜 End of Week 3 |
| Eval build | 🔜 Week 4 |

### Agents
| Agent | Status |
|---|---|
| Orchestrator | 🔜 Not started |
| Ticket Agent | 🔜 Not started |
| Comms Agent | 🔜 Not started |
| Blocker Agent | 🔜 Not started |
| Ceremony Agent | 🔜 Not started |
| Analytics Agent | 🔜 Not started |

---

## Learning Log (updated each session)

| Date | Concepts practised | Observations |
|---|---|---|
| 2026-05-24 | Multi-agent architecture, HITL patterns, north star metrics, eval sequencing, prompt caching, cost/latency tradeoffs, enterprise architecture, data residency, multi-tenancy | User independently arrived at prompt caching (called it "token balancer") before knowing the term — strong instinct. Chose velocity over activity metrics for north star without prompting — correct. Identified data residency and RBAC as enterprise security concerns unprompted. Pushed back on timeline appropriately when scope was added. |
