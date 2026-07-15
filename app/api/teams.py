from fastapi import APIRouter, Request, HTTPException
from app.models.events import InboundEvent, EventSource
from app.agents import orchestrator
from app.agents import ticket, comms, blocker, ceremony, analytics

router = APIRouter()

AGENT_MAP = {
    "ticket": ticket.handle,
    "comms": comms.handle,
    "blocker": blocker.handle,
    "ceremony": ceremony.handle,
    "analytics": analytics.handle,
}


@router.post("/api/teams/messages")
async def receive_teams_message(request: Request):
    """
    Receives inbound Teams activity payloads from Azure Bot Service.
    Passes the event to the orchestrator for classification and routing.
    """
    body = await request.json()

    activity_type = body.get("type", "")
    if activity_type != "message":
        return {"status": "ignored", "type": activity_type}

    event = InboundEvent(
        source=EventSource.teams,
        author_id=body.get("from", {}).get("id"),
        author_name=body.get("from", {}).get("name"),
        content=body.get("text", ""),
        metadata={"channel_id": body.get("channelId"), "conversation_id": body.get("conversation", {}).get("id")},
    )

    decision = orchestrator.route_event(event)
    handler = AGENT_MAP.get(decision.agent, comms.handle)
    result = handler(decision)

    return {
        "routed_to": decision.agent,
        "reasoning": decision.reasoning,
        "requires_hitl": decision.requires_hitl,
        "result": result,
    }
