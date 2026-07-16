import anthropic
import json
from app.models.events import RoutingDecision
from app.config import settings
from app.tools import jira_tools

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

TOOLS = [
    {
        "name": "get_sprint_health",
        "description": "Returns a health summary for the active sprint: total tickets, status breakdown, blocked count, story points completion percentage.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_blocked_tickets",
        "description": "Returns all tickets in the active sprint that are blocked, with assignee and last updated date.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_ungroomed_stories",
        "description": "Returns tickets in the active sprint missing story points, assignee, or description.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_team_velocity",
        "description": "Returns story points completed per sprint for the last N sprints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "num_sprints": {
                    "type": "integer",
                    "description": "Number of past sprints to include. Default 4.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_ticket_detail",
        "description": "Returns full detail for a specific ticket: description, acceptance criteria, comments, status, story points.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "The JIRA ticket ID, e.g. SSP-11",
                }
            },
            "required": ["ticket_id"],
        },
    },
    {
        "name": "jql_search",
        "description": "Fallback: executes a raw JQL query for freeform questions that don't map to a pre-built tool. Use only when no other tool fits.",
        "input_schema": {
            "type": "object",
            "properties": {
                "jql": {"type": "string", "description": "Valid JIRA JQL query string"},
                "max_results": {"type": "integer", "description": "Max tickets to return. Default 50."},
            },
            "required": ["jql"],
        },
    },
]

TOOL_MAP = {
    "get_sprint_health": lambda args: jira_tools.get_sprint_health(),
    "get_blocked_tickets": lambda args: jira_tools.get_blocked_tickets(),
    "get_ungroomed_stories": lambda args: jira_tools.get_ungroomed_stories(),
    "get_team_velocity": lambda args: jira_tools.get_team_velocity(args.get("num_sprints", 4)),
    "get_ticket_detail": lambda args: jira_tools.get_ticket_detail(args["ticket_id"]),
    "jql_search": lambda args: jira_tools.jql_search(args["jql"], args.get("max_results", 50)),
}

SYSTEM_PROMPT = """You are the Ticket Agent for AgileBot. You have access to tools that query a live JIRA instance.

When given a query:
1. Select the most appropriate tool. Prefer pre-built tools over jql_search.
2. Execute the tool and receive the data.
3. Summarise the result in plain English for the scrum master.

For action steps, blockers, and unblocking steps: use bullet points only.
For everything else: conversational."""


def handle(decision: RoutingDecision) -> dict:
    """
    Receives a routing decision, selects and executes the right JIRA tool,
    returns a plain English summary for the SM.
    """
    messages = [{"role": "user", "content": decision.event.content}]

    # Agentic tool-use loop — same ReAct pattern as research synthesizer
    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Haiku for tool selection — faster, cheaper
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            final_text = next(
                (b.text for b in response.content if hasattr(b, "text")), ""
            )
            return {"agent": "ticket", "response": final_text}

        if response.stop_reason == "tool_use":
            tool_block = next(b for b in response.content if b.type == "tool_use")
            tool_name = tool_block.name
            tool_args = tool_block.input

            try:
                tool_result = TOOL_MAP[tool_name](tool_args)
            except Exception as e:
                tool_result = {"error": str(e)}

            # Append assistant response and tool result to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": json.dumps(tool_result),
                }],
            })
        else:
            break

    return {"agent": "ticket", "response": "Unable to process JIRA query."}
