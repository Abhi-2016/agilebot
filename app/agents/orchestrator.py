import anthropic
from pathlib import Path
from app.models.events import InboundEvent, RoutingDecision
from app.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = Path("system_prompts/orchestrator.txt").read_text()

SPECIALIST_AGENTS = ["ticket", "comms", "blocker", "ceremony", "analytics"]


def route_event(event: InboundEvent) -> RoutingDecision:
    """
    Receives an inbound event, asks Claude to classify and route it,
    returns a RoutingDecision with the target agent and HITL flag.

    The system prompt is sent with cache_control so Claude caches it
    across calls — only the dynamic event content is reprocessed each time.
    """
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # prompt caching V1
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Source: {event.source}\n"
                    f"Author: {event.author_name or 'unknown'}\n"
                    f"Content: {event.content}\n"
                    f"Metadata: {event.metadata or {}}\n\n"
                    "Which agent should handle this event? "
                    "Reply in this exact format:\n"
                    "AGENT: <agent_name>\n"
                    "REASONING: <one sentence>\n"
                    "HITL: <yes or no>"
                ),
            }
        ],
    )

    raw = response.content[0].text
    agent, reasoning, hitl = _parse_routing(raw)

    return RoutingDecision(
        agent=agent,
        reasoning=reasoning,
        requires_hitl=hitl,
        event=event,
    )


def _parse_routing(raw: str) -> tuple[str, str, bool]:
    """Parses Claude's structured routing response."""
    lines = {
        line.split(":")[0].strip(): line.split(":", 1)[1].strip()
        for line in raw.strip().splitlines()
        if ":" in line
    }
    agent = lines.get("AGENT", "comms").lower()
    if agent not in SPECIALIST_AGENTS:
        agent = "comms"
    reasoning = lines.get("REASONING", "")
    hitl = lines.get("HITL", "no").lower() == "yes"
    return agent, reasoning, hitl
