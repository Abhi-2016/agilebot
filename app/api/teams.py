from fastapi import APIRouter, Request, HTTPException
from botframework.connector import ConnectorClient
from botframework.connector.auth import (
    MicrosoftAppCredentials,
    JwtTokenValidation,
    SimpleCredentialProvider,
)
from botbuilder.schema import Activity, ActivityTypes
from app.models.events import InboundEvent, EventSource
from app.agents import orchestrator
from app.agents import ticket, comms, blocker, ceremony, analytics
from app.config import settings

router = APIRouter()

AGENT_MAP = {
    "ticket": ticket.handle,
    "comms": comms.handle,
    "blocker": blocker.handle,
    "ceremony": ceremony.handle,
    "analytics": analytics.handle,
}

# Credential provider used by JwtTokenValidation to verify the incoming token
_credential_provider = SimpleCredentialProvider(
    settings.azure_bot_app_id,
    settings.azure_bot_app_password,
)


async def _verify_request(request: Request) -> None:
    """
    Validates the JWT token Azure Bot Service attaches to every request.
    Raises 401 if the token is missing or invalid — rejects non-Azure traffic.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    body = await request.body()
    activity = Activity().deserialize(await request.json())

    try:
        await JwtTokenValidation.authenticate_request(
            activity,
            auth_header,
            _credential_provider,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth failed: {e}")


def _send_reply(activity: Activity, text: str) -> None:
    """
    Sends a reply back into the Teams conversation using ConnectorClient.
    The reply appears in the same thread the SM sent the original message from.
    """
    credentials = MicrosoftAppCredentials(
        settings.azure_bot_app_id,
        settings.azure_bot_app_password,
        channel_auth_tenant=settings.azure_bot_tenant_id,
    )
    connector = ConnectorClient(credentials, base_url=activity.service_url)
    reply = Activity(
        type=ActivityTypes.message,
        text=text,
        conversation=activity.conversation,
        from_property=activity.recipient,
        recipient=activity.from_property,
        reply_to_id=activity.id,
    )
    connector.conversations.send_to_conversation(
        activity.conversation.id, reply
    )


@router.post("/api/teams/messages")
async def receive_teams_message(request: Request):
    """
    Receives inbound Teams activity payloads from Azure Bot Service.
    1. Verifies the Azure JWT signature — rejects anything not from Azure.
    2. Routes the event to the right specialist agent via the orchestrator.
    3. Sends the agent's response back into the Teams conversation.
    """
    body = await request.json()

    # Verify Azure signature before processing anything
    await _verify_request(request)

    activity_type = body.get("type", "")
    if activity_type != "message":
        return {"status": "ignored", "type": activity_type}

    activity = Activity().deserialize(body)

    event = InboundEvent(
        source=EventSource.teams,
        author_id=body.get("from", {}).get("id"),
        author_name=body.get("from", {}).get("name"),
        content=body.get("text", ""),
        metadata={
            "channel_id": body.get("channelId"),
            "conversation_id": body.get("conversation", {}).get("id"),
            "service_url": body.get("serviceUrl"),
        },
    )

    decision = orchestrator.route_event(event)
    handler = AGENT_MAP.get(decision.agent, comms.handle)
    result = handler(decision)

    # Build the reply text — use the agent's response if available, otherwise surface routing info
    reply_text = result.get("response") or f"Routed to {decision.agent} agent."

    # Send reply back into Teams
    _send_reply(activity, reply_text)

    return {
        "routed_to": decision.agent,
        "reasoning": decision.reasoning,
        "requires_hitl": decision.requires_hitl,
        "result": result,
    }
