# AgileBot

## Current Status

| Week | Focus | Status |
|---|---|---|
| Week 1 — Days 1-2 | FastAPI scaffold, orchestrator skeleton, prompt caching | ✅ Complete |
| Week 1 — Days 3-5 | JIRA integration, ticket grooming, alerts | 🔜 Next |
| Week 2 | Teams bot, intent detection, standup, blocker HITL | 🔜 Pending |
| Week 3 | Ceremonies, metrics, eval suite design | 🔜 Pending |
| Week 4 | Eval suite build (fast follow) | 🔜 Pending |

**North star:** Sprint velocity +15% within 3 months of deployment.

---

## What is AgileBot?

AgileBot is an agentic AI scrum master built on the Claude Agent SDK. It removes the rote administrative work that consumes most of a scrum master's time — logging tickets, chasing status updates, sending repeated emails, following up with developers and stakeholders — so the SM can focus on what actually matters: surfacing problems early, helping the team unblock, and developing a deep enough understanding of the product to contribute meaningfully.

AgileBot lives inside Microsoft Teams. It watches, listens, acts, and always surfaces decisions to the SM before taking any consequential action.

---

## What it does

- **Blocker detection** — picks up "I'm stuck" signals in Teams chat and from stale JIRA tickets; proposes proportionate resolution steps for SM approval
- **Ticket grooming** — daily JIRA sweep, flags unpointed or unassigned stories, enforces templates
- **Async standup** — collects updates via Teams, summarises, flags blockers to the SM
- **Ceremonies** — sprint planning, retrospective clustering, sprint review summaries
- **Analytics** — velocity, blocker trends, sentiment — all figures traceable to JIRA source data, no hallucination

---

## Architecture

Supervisor + specialist multi-agent pattern. One Orchestrator owns all inbound events and human-in-the-loop (HITL) approval gates. Five specialist agents handle distinct domains.

```
┌─────────────────────────────────────┐
│         ORCHESTRATOR AGENT          │
│  Routes events · Owns HITL gates    │
└──┬─────────┬────────┬────────┬──────┘
   │         │        │        │        │
TICKET    COMMS   BLOCKER  CEREMONY  ANALYTICS
AGENT     AGENT   AGENT    AGENT     AGENT
```

Events arrive from three sources: **Microsoft Teams messages**, **JIRA updates**, and **scheduled triggers** (cron jobs). The orchestrator classifies each event, routes to the right specialist, and gates any consequential action through SM approval.

See [PLAN.md](./PLAN.md) for full architecture decisions and rationale.

---

## Stack

| Layer | Choice |
|---|---|
| Agent runtime | Claude API (claude-opus-4) + Claude Agent SDK |
| Backend | FastAPI (Python) |
| Bot framework | botbuilder-python (Azure Bot Service) |
| Interface | Microsoft Teams (Adaptive Cards) |
| Ticketing | JIRA REST API |
| Database | PostgreSQL (Supabase) + Redis |
| Auth | Azure AD (M365 ecosystem) |

---

## Running Locally

```bash
# 1. Clone and create virtual environment
git clone https://github.com/Abhi-2016/agilebot.git
cd agilebot
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Fill in your keys in .env

# 4. Start the server
uvicorn app.main:app --reload

# 5. Verify
curl http://localhost:8000/health
# {"status":"ok","service":"agilebot"}
```

---

## Learning Log

This project is built as a portfolio piece for an Agentic AI Product Builder career. This log captures key learnings — decisions made, what worked, what didn't, and why.

| Date | Learning |
|---|---|
| 2026-05-22 | **Outcome metrics over activity metrics.** Chose sprint velocity (+15% in 3 months) as north star rather than "tickets logged by bot." Activity metrics are easy to hit and easy to game. Velocity forces honest measurement of whether the tool is actually helping. |
| 2026-05-22 | **Track failure modes separately.** Blocker detection via chat inference and via ticket cadence check are tracked as separate metrics — if both go wrong the fixes are different, and combining them hides signal. |
| 2026-05-22 | **Eval sequencing matters.** Eval suite ships in Week 4 but is *designed* in Week 3. Evaluating behaviour that is still changing is wasted effort — but pushing design to after ship means it never happens. |
| 2026-05-22 | **Scope control is a product decision, not a compromise.** JIRA only, Teams only for MVP — not because other integrations don't matter, but because one integration done well proves the pattern. Expand once proven. |
| 2026-05-22 | **Multi-agent isn't just about capability — it's about security and maintainability.** Chose supervisor + specialist over monolithic for three distinct reasons: separation of concerns, token management, and least-privilege security. Each justification stands independently. |
| 2026-07-15 | **Interface before implementation.** Built all five specialist agents as stubs with defined input/output contracts before writing any logic. The orchestrator routes correctly against stubs — logic fills in without breaking the flow. |
| 2026-07-15 | **Prompt caching is a Day 1 decision, not a retrofit.** Added `cache_control` on the orchestrator system prompt from the first commit. Baking cost efficiency in early costs nothing extra. Adding it later requires touching every agent call. |
| 2026-07-15 | **Webhooks over polling.** Teams pushes events to AgileBot rather than AgileBot polling Teams. Lower latency, lower resource usage, simpler code — and the right mental model for event-driven agentic systems. |
