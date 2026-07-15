from app.models.events import RoutingDecision


def handle(decision: RoutingDecision) -> dict:
    """Stub — standup, retro, planning logic in Week 3."""
    return {"agent": "ceremony", "status": "stub", "event": decision.event.content}
