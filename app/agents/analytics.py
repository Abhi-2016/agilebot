from app.models.events import RoutingDecision


def handle(decision: RoutingDecision) -> dict:
    """Stub — JIRA-sourced metrics and reporting in Week 3."""
    return {"agent": "analytics", "status": "stub", "event": decision.event.content}
