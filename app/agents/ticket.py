from app.models.events import RoutingDecision


def handle(decision: RoutingDecision) -> dict:
    """Stub — full JIRA read/write logic in Week 1 Day 3-4."""
    return {"agent": "ticket", "status": "stub", "event": decision.event.content}
