# AgileBot — Project Plan

## Problem Statement

AgileBot exists to remove the rote work that scrum masters spend most of their time on — logging tickets, chasing updates, sending repeated emails, following up with team members and stakeholders. By automating that layer entirely, AgileBot frees the SM (or whoever is playing the role) to do the work that actually matters: surfacing problems early, helping the team solve them, and developing a deep enough understanding of the product to contribute meaningfully — not just facilitate.

---

## Ground Rules

1. PLAN.md, CLAUDE.md, and README.md are updated after every commit to reflect what has been achieved.
2. All system prompts are written by the user and reviewed by Claude.
3. Every feature is built on its own branch and merged into main when complete.
4. The user drives all decisions. Claude asks questions and guides — the user makes decisions.
5. A robust eval suite is built alongside the product. The user makes eval decisions; Claude reviews and guides.
6. Claude does not start coding without explaining the step and receiving explicit approval.
7. These ground rules are followed without deviation.
8. Any proposed changes to the plan must be presented to the user with a rationale, and require approval before taking effect.
9. **Learning goal:** The user's aim is to become an Agentic AI Product Builder. Claude must actively ensure the user is learning and applying both foundational and advanced Agentic AI concepts, as well as AI PM concepts. Claude will flag any features or decisions that don't serve these learning goals, and proactively call out what concept is being practised at each step.
10. **Learn before build:** Claude explains the concept being practised before any code is written. The user must understand the why before seeing the how.
11. **Guided discovery:** For PM exercises (metrics, evals, specs, etc.), Claude leads with questions and the user provides the answers. Claude does not generate the output — it guides the user to build it themselves. Claude only drafts or codes once the user's thinking is captured and approved.
12. **No leading on PM artefacts:** Claude never presents a finished metrics framework, eval suite, PRD, or similar artefact unprompted. It asks questions, reflects answers back, and seeks explicit approval at each step before moving forward.
13. **Honest feedback:** Claude is not sycophantic. Claude pushes back when rationale is weak, flags decisions with unacknowledged tradeoffs, and challenges unmeasurable metrics. Equally, Claude explicitly calls out strong product thinking and explains why it is strong. The user is here to learn — agreement without challenge is not useful.
14. **Eval design before ship:** The eval suite scoring rubrics, judge prompts, and pass/fail thresholds must be designed in Week 3 even if the suite is not built until Week 4. "Fast follow" is only acceptable if the design work is done first.
15. **Living learning log:** PLAN.md, CLAUDE.md, and README.md each maintain a learning log that is updated after every commit. The log captures: concepts practised, decisions taken (and why), what went wrong and what was learned from it, and moments of strong product thinking. This project is a portfolio artefact — the log must be honest, specific, and useful to someone reading it cold. Claude is responsible for prompting the user to reflect and update the log after each meaningful milestone.

---

## Architecture

### Why Supervisor + Specialist (not monolithic)

We chose a multi-agent architecture over a single agent for three reasons:

1. **Separation of concerns** — each agent owns one domain and does it well. Easier to build, test, debug, and improve independently.
2. **Token management** — focused agents have smaller, tighter context windows. One agent holding everything would bloat context and degrade output quality.
3. **Security** — specialist agents only have access to the tools and data they need. The Comms Agent has no access to JIRA credentials. The Ticket Agent cannot read chat messages.

### Why Microsoft Teams (not a custom dashboard)

The company this is being built for uses Microsoft Teams and the M365 platform. No adoption friction — the bot lives where the team already works. The M365 ecosystem also unlocks Outlook Calendar, email, and Teams meeting transcripts under a single auth setup, which expands AgileBot's surface area in later phases for free.

### Why JIRA only (MVP)

The target company uses JIRA. Starting with one integration done well is more valuable than three integrations done poorly. The pattern is proven first, then expanded to Linear, Azure DevOps, and Shortcut in later phases.

### JIRA Integration Approach — Pre-built Tool Functions (Option 2)

Three options were evaluated:

| Option | Approach | Verdict |
|---|---|---|
| 1 — NL → JQL | LLM translates natural language to JQL, executes against JIRA REST API | Fallback only — flexible but LLM can generate invalid JQL |
| 2 — Pre-built tools | Specific tool functions per use case (get_sprint_health, get_blocked_tickets, etc.) | **Primary approach** — reliable, testable, eval-able |
| 3 — Atlassian MCP | Native MCP connector, no custom HTTP wrappers | Enterprise phase — less control, token bloat risk without filtering |

**Decision: Option 2 as foundation, Option 1 as fallback for freeform queries.**

Pre-built tools cover 90% of AgileBot's JIRA needs. For the 10% of freeform questions, the LLM falls back to JQL generation with validation before execution.

### JIRA Query Modes — Both Supported

Two distinct query modes, both required:

1. **SM-initiated query** — SM asks `@AgileBot what's blocking the sprint?` in Teams. Ticket Agent selects the right tool and returns a plain English summary.
2. **Proactive report** — AgileBot runs on a schedule (cron), generates sprint health and grooming reports automatically, posts to Teams without being asked.

### JIRA Tool Functions (MVP)

| Function | What it does | Triggered by |
|---|---|---|
| `get_sprint_health()` | Current sprint: open tickets, blocked count, completion % | SM query + scheduled report |
| `get_blocked_tickets()` | All tickets flagged as blocked with assignee and age | SM query + blocker detection cadence |
| `get_ungroomed_stories()` | Tickets missing story points, assignee, or description | Scheduled daily sweep |
| `get_team_velocity()` | Story points completed per sprint over last N sprints | SM query + weekly digest |
| `get_ticket_detail(ticket_id)` | Full story detail: description, AC, comments, status | SM query + blocker analysis |

---

## Agent Map

```
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR AGENT                        │
│  Routes inbound events → specialist agents                  │
│  Maintains global sprint state                              │
│  Owns all HITL approval gates                               │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌──────┐ ┌───────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│TICKET│ │COMMS  │ │CEREMONY│ │BLOCKER │ │ANALYTICS │
│AGENT │ │AGENT  │ │AGENT   │ │AGENT   │ │AGENT     │
└──────┘ └───────┘ └────────┘ └────────┘ └──────────┘
```

| Agent | Responsibility |
|---|---|
| **Orchestrator** | Owns all inbound events. Routes to specialists. Manages HITL approval flow. Holds sprint state. |
| **Ticket Agent** | JIRA read/write. Ticket creation, grooming checks, status updates, dependency mapping. |
| **Comms Agent** | Monitors Teams channels. Intent detection (blocker / book call / log defect). Sentiment analysis. Concise update summaries. |
| **Blocker Agent** | Detects blockers via chat inference and proactive ticket cadence checks. Generates proportionate resolution steps. Drafts actions (emails, messages) for SM approval. |
| **Ceremony Agent** | Async standup collection and summary. Sprint planning. Retrospective clustering. Sprint review summaries. Suggests the right ceremony for the moment in the sprint. |
| **Analytics Agent** | Pulls data from JIRA. Presents velocity, throughput, blocker trends, and sentiment. Does not hallucinate — every figure must be traceable to source data. |

---

## Interface

**Primary UI:** Microsoft Teams (Adaptive Cards)
**Secondary:** JIRA (for ticket actions)
**Future:** Outlook Calendar, Teams meeting transcripts, email (via Microsoft Graph API)

### Bot Commands

```
@AgileBot standup          → triggers async standup collection
@AgileBot blocked [desc]   → blocker intake + analysis
@AgileBot retro            → opens retro card collection
@AgileBot sprint status    → current sprint health summary
@AgileBot groom [ticket]   → groom a specific JIRA ticket
@AgileBot digest           → weekly metrics summary
```

---

## HITL Approval Matrix

| Action | Auto-execute | Needs SM Approval |
|---|---|---|
| Post standup summary | ✅ | |
| Flag under-groomed ticket | ✅ | |
| Generate retro clusters | ✅ | |
| Comment on JIRA ticket | ✅ | |
| Suggest blocker resolution steps | ✅ | |
| Send stakeholder digest | ✅ | |
| Draft reminder email | ✅ (draft only) | ✅ (send) |
| Move ticket status | | ✅ |
| Assign ticket to person | | ✅ |
| Book / cancel calendar events | | ✅ |
| Send external email | | ✅ |
| Escalate to leadership | | ✅ |

---

## Success Metrics

### North Star — Sprint Velocity Growth
**Target: +15% within 3 months of deployment**

Measured as: average story points completed per sprint (rolling 4-week window) vs. baseline at deployment date.

**Why velocity:** If AgileBot is removing admin friction, catching blockers early, and keeping tickets well-groomed, the team should ship more. Velocity is the output that proves the tool is working — not just active.

**Known assumption:** Velocity can be influenced by factors outside AgileBot's control (team size changes, scope creep, technical debt). Any sprint where an external factor skews the number must be flagged and excluded from the trend.

---

### Product Metrics

| Metric | What it measures | How to measure |
|---|---|---|
| Blocker detection rate — chat inference | % of real blockers caught via language signals in Teams | Compare agent-flagged blockers vs. blockers later self-reported — gaps are misses |
| Blocker detection rate — ticket cadence | % of stale tickets that had a real blocker behind them | Proactive check results vs. developer confirmation |
| Admin automation rate | % of JIRA updates, status changes, and ticket logs made by bot vs. human | JIRA activity log — author = AgileBot vs. human |
| Blocker resolution time | Time from blocker detected → SM actioned → team unblocked | Timestamps in blockers table |
| SM response time to HITL cards | How quickly SM approves / rejects Adaptive Cards | Teams card interaction timestamps |
| Team self-service rate | How often team queries AgileBot directly instead of pinging a person | Bot query logs vs. direct DMs to SM |

---

### AI Quality Metrics

| Signal | What it catches |
|---|---|
| Blocker detection false positive rate | Agent flags something as a blocker that isn't — erodes SM trust over time |
| HITL rejection rate | SM rejects proposed steps — indicates agent reasoning is off |
| Ticket grooming accuracy | % of flagged tickets that were genuinely under-groomed vs. false flags |
| Intent classification accuracy | Agent correctly identifies "book a call" vs. "log a defect" vs. "blocker" |
| Analytics accuracy | Any figure that doesn't match JIRA source data is a hard fail |

---

## Eval Suite

**Shipping:** Week 4 (fast follow)
**Design deadline:** End of Week 3 — rubrics, judge prompts, and pass/fail thresholds must be defined before MVP ships.

| Agent | Eval | Pass Criteria | Fail Signal |
|---|---|---|---|
| **Ticket Agent** | Ticket creation from tagged request | Ticket created in JIRA with all required fields | Missing fields → error thrown, not silent failure |
| **Comms Agent** | Sprint update summary quality | Concise, high-level, covers all active tickets | Exceeds length threshold, repeats information, or misses an active ticket |
| **Blocker Agent** | Unblocking step proportionality | Steps are actionable and proportionate to blocker severity | Disproportionate escalation (e.g. VP for a missing API key) or vague steps |
| **Ceremony Agent** | Right ceremony for sprint moment | Correct ceremony suggested given sprint day and context | Planning suggested mid-sprint; retro before sprint ends |
| **Analytics Agent** | Data accuracy | All figures traceable to current JIRA state | Any hallucinated or stale number is a hard fail |

### Blocker Agent — Eval Pattern (LLM-as-Judge)

```
1. Blocker detected (chat inference or ticket cadence check)
2. Blocker Agent generates resolution steps
3. LLM-as-judge scores steps:
   - Are they proportionate to blocker severity?
   - Are they actionable without additional information?
   - Is the right person / team being involved?
4. Score passes threshold → draft action prepared (email, Teams message, JIRA comment)
5. Adaptive Card surfaced to SM:
   - Blocker summary
   - Proposed steps + judge score
   - Draft action (e.g. full email body)
   - [Approve & Send] [Edit] [Escalate]
6. SM hits send. AgileBot executes.
```

**The SM never writes from scratch — only reviews and approves.**

---

## 3-Week MVP Build Plan

### Week 1 — Core Infrastructure + JIRA
| Day | Work |
|---|---|
| 1–2 | Project scaffold. FastAPI. PostgreSQL schema. Claude Agent SDK orchestrator skeleton. |
| 2 | **Prompt caching (Version 1)** — add `cache_control` to all static system prompts at build time. Not bolted on later. |
| 3–4 | JIRA integration (read/write). Ticket grooming checks against template. |
| 5 | JIRA → Teams alerts for missing story points, unassigned tickets. |

### Week 2 — Teams Bot + Blocker Intelligence
| Day | Work |
|---|---|
| 6–7 | Azure Bot Service setup. Teams webhook listener. Intent detection (blocker / book call / log defect). |
| 8–9 | Async standup collection + summary generation. Blocker Agent: analyze + propose steps. |
| 10 | HITL Adaptive Card approval flow (approve / edit / escalate). |

### Week 3 — Ceremonies + Eval Design + Polish
| Day | Work |
|---|---|
| 11–12 | Sprint planning helper (velocity, capacity, backlog suggestions). |
| 13–14 | Retro collection + theme clustering. Basic metrics: velocity, blockers, sentiment. |
| 15 | Eval rubrics + judge prompts designed. End-to-end testing. Bug fixes. Demo prep. |

### Week 4 — Eval Suite (Fast Follow)
- Build and wire LLM-as-judge for Blocker Agent
- Implement pass/fail thresholds across all 5 agents
- First eval run against real sprint data

---

## Enterprise Phase

**Sequencing rationale:** Enterprise hardening begins only after the MVP is proven with a real team. Building enterprise features before the core product is validated is wasted effort. The right order is: MVP → prove value → harden → go to market.

**Trigger to start this phase:** MVP has been running with at least one real team for 4+ weeks and velocity metric is trending positively.

### E1 — Multi-Tenancy
Every company gets an isolated tenant. Separate DB schemas per tenant. No cross-tenant data access is architecturally possible. Tenant provisioning via admin portal.

### E2 — Prompt Caching (Version 2 — Semantic Cache)
Redis layer that catches semantically similar queries before they reach the LLM. "What's the sprint status?" asked by 10 developers = 1 LLM call, not 10. Built on top of Version 1 (static prompt caching already in MVP).
- Embedding similarity check on every inbound query
- Cache hit threshold: configurable per agent
- Estimated additional savings: 20–30% on top of Version 1

### E3 — Horizontal Scaling + Async Job Queue
| Current (MVP) | Enterprise |
|---|---|
| Single FastAPI instance | Multiple instances behind AWS ALB load balancer |
| Requests handled inline | Celery + Redis async job queue for heavy tasks |
| | Auto-scaling based on request volume |
| | JIRA sweeps and analytics runs moved to background jobs |

### E4 — Security Hardening
| Concern | Solution |
|---|---|
| Data encryption | TLS 1.3 in transit, AES-256 at rest |
| Identity | Full SAML SSO via Azure AD — no separate credentials |
| Authorisation | RBAC middleware on every endpoint — team-scoped data |
| Audit logs | Every agent action logged with timestamp, actor, and outcome — exportable for legal |
| DDoS protection | Cloudflare in front of all endpoints |
| WAF | Web Application Firewall on all inbound traffic |

### E5 — Data Residency
Region selector at tenant onboarding. EU / Canada / US deployments. Data never leaves the chosen region. Supabase instances pinned per region.

### E6 — Compliance Certifications
SOC 2 Type II, GDPR, ISO 27001. Third-party audited. Required before enterprise procurement will evaluate the tool. Not optional — plan the certification process 3–6 months before go-to-market.

### E7 — Distribution
Microsoft Teams App Store listing. One-click tenant-wide deployment. IT admin approval flow built in. Automatic version updates.

---

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Agent Runtime | Claude API (claude-opus-4) | Tool use, long context, multi-agent |
| Orchestration | Claude Agent SDK | Multi-agent coordination |
| Backend | FastAPI (Python) | Async, webhook handling |
| Bot Framework | botbuilder-python | Azure Bot Service + Teams integration |
| Primary DB | PostgreSQL (Supabase) | Managed, zero-ops, realtime |
| Cache / State | Redis | Active sprint state, rate limits |
| Auth | Azure AD | M365 ecosystem, single auth for Teams + Graph API |
| Hosting | Railway (MVP) → AWS ECS (scale) | Simple Docker-based start |
| Observability | LangSmith + Datadog | Agent traces + infra metrics |

---

## Database Schema (MVP)

```sql
teams         -- team config, JIRA project key, Teams channel ID
members       -- name, Teams ID, JIRA ID, role
sprints       -- active sprint per team, goal, dates, velocity
blockers      -- detected blockers, source, resolution state, timestamps
ceremonies    -- standup / retro records, summaries
action_items  -- from retros, tracked across sprints, recurring flag
```

---

## Learning Log

This log is updated after every meaningful milestone. It is honest — it captures what went wrong as well as what went right. It exists to demonstrate how product thinking develops over time, not just what was built.

| Date | Concept practised | Decision taken | Right or wrong | What was learned |
|---|---|---|---|---|
| 2026-05-22 | Multi-agent architecture | Supervisor + specialist pattern over monolithic agent | ✅ Right | Separation of concerns, token management, and security are three distinct justifications for multi-agent — not the same argument stated three ways |
| 2026-05-22 | North star metric selection | Sprint velocity (+15% in 3 months) over activity metrics (tickets logged by bot) | ✅ Strong product sense | Outcome metrics prove value. Activity metrics are easy to hit and easy to game. Velocity forces honest measurement |
| 2026-05-22 | Metric granularity | Track chat-inference blocker detection and ticket-cadence detection separately | ✅ Right | If both go wrong, the fixes are different. Combining them hides signal |
| 2026-05-22 | Eval sequencing | Ship eval suite in Week 4, design it in Week 3 | ✅ Right | Evaluating behaviour that is still changing is wasted effort. But design must happen before ship — "fast follow" without a design date becomes never |
| 2026-05-22 | Scope control | JIRA only for MVP, Teams only for MVP | ✅ Right | One integration done well beats three done poorly. Prove the pattern, then expand |
| 2026-07-18 | LLM output parsing | Added fuzzy normalization to `_parse_routing()` in orchestrator.py | ✅ Right | LLMs don't always format output exactly as instructed. A silent fallback (`agent = "comms"`) masked a correct reasoning response — the LLM knew the right answer, the parser discarded it. Fix: strip " agent" suffix and normalize synonyms before validating. Production standard: JSON mode, fuzzy normalization, or an explicit "unknown" state. Never a silent default. |
| 2026-07-18 | System prompt precision | Added explicit routing decision rules to orchestrator system prompt | ✅ Right | Agent descriptions that say what an agent "owns" are insufficient for routing. The LLM needs explicit if/then routing rules, especially for overlapping concepts (blocker-the-noun vs. blocker-the-agent, JIRA data query vs. Comms Agent). The gap between good reasoning and correct output is often a parsing or prompt precision problem — not a model intelligence problem. |

---

## Progress Log

| Date | Milestone |
|---|---|
| 2026-05-22 | Project initiated. Problem statement defined. Architecture decided. Agent map confirmed. Success metrics and eval suite designed. Ground rules set. PLAN.md created. |
| 2026-07-15 | Orchestrator system prompt written by user and reviewed by Claude. |
| 2026-05-24 | Enterprise phase designed. Prompt caching (Version 1) added to MVP Day 2. Enterprise phase sequenced deliberately after MVP validation — not built in parallel. |
| 2026-07-15 | Week 1 Day 1-2 complete. FastAPI scaffold, orchestrator skeleton, prompt caching, 5 specialist stubs, PostgreSQL schema, Supabase client. PR #1 merged. /health endpoint verified locally. |
| 2026-07-18 | JIRA tool functions complete. Ticket Agent agentic loop wired. Orchestrator routing bug (silent fallback masking) debugged and fixed. Routing decision rules added to orchestrator system prompt. feature/week1-jira-integration in progress. |

---

## Learning Log

### Concepts Practised

| Concept | Where | Notes |
|---|---|---|
| Supervisor + specialist architecture | Agent map design | User independently reasoned separation of concerns, token management, and security as justification — without being prompted |
| Human-in-the-loop (HITL) patterns | HITL approval matrix | Designed the right boundary between auto-execute and SM approval. SM reviews drafts, never writes from scratch. |
| Prompt caching | MVP Day 2 + Enterprise E2 | User independently arrived at the concept of token load balancing before knowing the term. Version 1 (static cache) in MVP. Version 2 (semantic cache) in enterprise. |
| Multi-tenancy | Enterprise phase | User identified data isolation as a security concern unprompted. Extended to RBAC and team-scoped access. |
| Data residency | Enterprise phase | User named geographic data constraints (Canada example) without prompting. Strong real-world product awareness. |
| Cost and latency tradeoffs | Prompt caching decision | User chased 60-80% savings as a product decision, not just an engineering one. Correct instinct. |
| Eval strategy | Eval suite design | LLM-as-judge chosen for Blocker Agent. Eval design deadline set before ship. Fast follow sequenced correctly. |
| Prompt caching V1 implementation | orchestrator.py | cache_control added to static system prompt from first commit. Baking cost efficiency in early costs nothing extra — retrofitting touches every agent. |
| Webhook pattern | Teams endpoint | Teams pushes events to AgileBot rather than AgileBot polling. Lower latency, lower resource usage, correct mental model for event-driven agentic systems. |
| Interface before implementation | Stub agents | All 5 specialist agents built as stubs with defined contracts. Orchestrator routes correctly end-to-end before any specialist logic exists. |
| Silent fallback masking | orchestrator.py `_parse_routing()` | When a parser silently falls back to a default on failure, the LLM's correct reasoning gets discarded invisibly. The system appeared to work (returned a result) but was wrong. Fix: explicit normalization + raise on unknown, not silent default. |
| System prompt routing precision | orchestrator.txt | Agent descriptions are not sufficient for reliable routing in a multi-agent system. Explicit if/then routing rules are required — particularly when agent names overlap with domain concepts (e.g. "Blocker Agent" vs. questions about blockers). |

### Strong Product Decisions

| Decision | Why it was good |
|---|---|
| Velocity as north star metric | Outcome metric, not activity metric. Harder to game, directly tied to team value. Most PMs pick the easier activity metric. |
| Track blocker detection methods separately | Correct. Different failure modes require different fixes. Combining them would hide signal. |
| Prompt caching in MVP, not post-MVP | Baking cost efficiency in from Day 1 rather than retrofitting it. Shows cost awareness as a first-class concern. |
| Enterprise phase sequenced after MVP validation | Avoids the common trap of over-engineering before proving value. Shows build sequencing maturity. |
| Teams as UI instead of custom dashboard | Eliminated an entire frontend build. Reduced adoption friction. Leveraged existing M365 auth. |
| Interface before implementation (stubs) | Built all 5 specialist agents as stubs with defined contracts before writing any logic. Orchestrator routes end-to-end correctly — logic fills in later without breaking the flow. |

### Decisions Challenged / Pushed Back On

| Decision | Challenge | Outcome |
|---|---|---|
| 3-week MVP timeline | Aggressive given eval suite scope | Eval suite moved to Week 4 fast follow. Design still required by end of Week 3. |
| Eval suite in MVP | Would bloat scope and evaluate unstable behaviour | Moved to Week 4. Design deadline held firm. |
