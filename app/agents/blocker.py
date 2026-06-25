from app.models.events import RoutingDecision


def handle(decision: RoutingDecision) -> dict:
    """Stub — blocker detection and resolution steps in Week 2."""
    return {"agent": "blocker", "status": "stub", "event": decision.event.content}
