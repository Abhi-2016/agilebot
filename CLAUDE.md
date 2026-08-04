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

| Decision Area | What was decided | Why |
|---|---|---|
| **Agent pattern** | Supervisor + specialist (Orchestrator + 5 specialists), not monolithic | Separation of concerns — each agent owns one domain; token management — focused agents have tighter context; security isolation — Comms Agent has no JIRA credentials |
| **Primary interface** | Microsoft Teams (Adaptive Cards) instead of Slack or custom dashboard | Company uses M365 — no adoption friction, bot lives where the team already works; single Azure AD auth unlocks Outlook, Graph API, and Teams transcripts for free |
| **Ticketing system (MVP)** | JIRA only | Company uses JIRA; one integration proven well beats three done poorly; proves the pattern before expanding |
| **JIRA integration pattern** | Pre-built tool functions as primary, JQL generation as fallback | Pre-built tools are reliable, testable, and eval-able for 90% of use cases; JQL fallback handles freeform queries without over-engineering |
| **Atlassian MCP** | Deferred to enterprise phase | Less control over what is fetched; token bloat risk without filtering; pre-built tools give tighter scope for MVP |
| **JIRA query modes** | Both SM-initiated (Teams) and proactive scheduled (cron) | SM asks in real time; AgileBot also generates reports unprompted — both modes needed for full automation |
| **Backend framework** | FastAPI (Python) | Async, webhook-ready, lightweight; matches Python AI ecosystem |
| **Database** | PostgreSQL via Supabase | Managed, zero-ops, realtime capabilities, row-level security built in |
| **Cache layer** | Redis | Sprint state, rate limiting, async job queue |
| **Auth** | Azure AD | M365 ecosystem; SSO; unlocks Microsoft Graph API for calendar, email, and meetings in later phases |
| **Bot framework** | Azure Bot Service + botbuilder-python | Required for Teams channel integration; handles auth and message routing from M365 |
| **Hosting** | Railway for MVP → AWS ECS for scale | Railway is Docker-based with zero-ops for MVP; ECS with ALB load balancer and auto-scaling for enterprise |
| **Observability** | LangSmith + Datadog | LangSmith traces agent calls and tool use; Datadog covers infra metrics |
| **Prompt caching — V1** | `cache_control` on all static system prompts from Day 1 | 60% cost reduction on repeated orchestrator calls; baked in at build time, not retrofitted — retrofitting touches every agent call |
| **Prompt caching — V2** | Semantic cache via Redis embeddings (enterprise phase) | Additional 20–30% savings; catches semantically similar queries before they reach the LLM; built on top of V1 |
| **LLM model tiers** | claude-opus-4-5 for orchestrator, claude-haiku-4-5 for Ticket Agent tool selection | Haiku is faster and cheaper for structured tool selection decisions; Opus for complex routing and reasoning |
| **Webhook pattern** | Teams pushes events to AgileBot, not AgileBot polling Teams | Lower latency, lower resource usage, simpler code; correct mental model for event-driven agentic systems |
| **Orchestrator routing rules** | Explicit if/then routing rules in system prompt, not just agent descriptions | Agent descriptions alone are insufficient — overlapping domain language causes misroutes; LLM needs explicit decision rules for ambiguous cases |
| **LLM output parsing** | Fuzzy normalization in parser, not silent fallback | Silent fallback masked failures — system appeared to work but was routing incorrectly; explicit normalization surfaces parsing errors visibly |
| **HITL boundary** | SM approves: ticket moves, assignments, calendar events, emails, escalations. Auto-execute: summaries, flags, drafts, comments | SM never writes from scratch — only reviews and approves consequential actions; rote output is fully automated |
| **Eval timing** | Design in Week 3, build in Week 4 | Evaluating unstable behaviour is wasted effort; but "fast follow" without a design date means it never happens |
| **Enterprise phase sequencing** | Enterprise hardening begins only after MVP is validated with a real team | Avoid over-engineering before value is proven; right order is MVP → prove value → harden → go to market |
| **Multi-tenancy (enterprise)** | Separate DB schemas per tenant | No cross-tenant data access is architecturally possible — not just a policy |
| **Data residency (enterprise)** | Region selector at onboarding — EU / Canada / US | Data never leaves the chosen region; required for enterprise procurement in regulated industries |
| **Compliance (enterprise)** | SOC 2 Type II, GDPR, ISO 27001 — third-party audited | Required before enterprise procurement will evaluate the tool; plan certification 3–6 months before go-to-market |

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

### Current Phase: Week 1 — JIRA Integration (Days 3–5)
| Item | Status |
|---|---|
| PLAN.md | ✅ Complete |
| CLAUDE.md | ✅ Complete |
| README.md | ✅ Complete |
| Repo on GitHub | ✅ Live — https://github.com/Abhi-2016/agilebot |
| FastAPI scaffold | ✅ Complete — PR #1 merged |
| Orchestrator skeleton | ✅ Complete — PR #1 merged |
| Prompt caching (V1) | ✅ Complete — cache_control on orchestrator system prompt |
| JIRA integration | 🔄 In progress — feature/week1-jira-integration |
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
| 2026-07-15 | Agentic tool-use loop, webhook pattern, prompt caching V1 implementation, interface before implementation, Pydantic validation at system boundaries, health check pattern | Built and merged PR #1. FastAPI scaffold complete. Orchestrator skeleton wired with cache_control. /health verified. All 5 specialist agents stubbed with defined contracts. Teams webhook endpoint receives and routes events end-to-end. |
| 2026-07-18 | LLM output parsing robustness, system prompt routing precision, silent fallback masking | JIRA tool functions complete. Ticket Agent agentic loop live. Debugged orchestrator routing: LLM was reasoning correctly ("Ticket Agent") but parser was silently falling back to "comms" because "Ticket Agent" ≠ "ticket". Fix: fuzzy normalization in `_parse_routing()`. Key concept: the gap between correct LLM reasoning and correct system output is often a parsing problem, not a model problem. |
