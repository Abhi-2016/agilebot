# AgileBot

An agentic scrum master built on the Claude Agent SDK. AgileBot automates the rote work of sprint management — ticket logging, status chasing, blocker detection, ceremony facilitation — so the scrum master can focus on coaching the team and understanding the product.

## What it does

- **Ticket grooming** — daily JIRA sweep, flags unpointed or unassigned stories, enforces templates
- **Blocker detection** — picks up "I'm stuck" signals in Teams chat and from stale tickets; proposes resolution steps for SM approval
- **Async standup** — collects updates via Teams, summarises, flags blockers
- **Ceremonies** — sprint planning, retrospective clustering, sprint review summaries
- **Analytics** — velocity, blocker trends, sentiment — all traceable to JIRA source data

## Stack

| Layer | Choice |
|---|---|
| Agent runtime | Claude API (claude-opus-4) + Claude Agent SDK |
| Backend | FastAPI (Python) |
| Bot framework | botbuilder-python (Azure Bot Service) |
| Interface | Microsoft Teams (Adaptive Cards) |
| Ticketing | JIRA REST API |
| Database | PostgreSQL (Supabase) + Redis |
| Auth | Azure AD |

## Architecture

Supervisor + specialist multi-agent pattern. One Orchestrator owns all inbound events and human-in-the-loop approval gates. Five specialist agents handle distinct domains: Ticket, Comms, Blocker, Ceremony, Analytics.

See [PLAN.md](./PLAN.md) for full architecture, agent map, and decision rationale.

## Project Status

MVP target: 3 weeks. Eval suite: Week 4 fast follow.

See [PLAN.md](./PLAN.md) for the full build plan and progress log.

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
