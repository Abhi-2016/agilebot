from app.models.events import RoutingDecision


def handle(decision: RoutingDecision) -> dict:
    """Stub — intent detection and sentiment analysis in Week 2."""
    return {"agent": "comms", "status": "stub", "event": decision.event.content}
