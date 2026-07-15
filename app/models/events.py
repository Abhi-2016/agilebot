from pydantic import BaseModel
from typing import Optional
from enum import Enum


class EventSource(str, Enum):
    teams = "teams"
    jira = "jira"
    scheduled = "scheduled"


class InboundEvent(BaseModel):
    source: EventSource
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    content: str
    metadata: Optional[dict] = None


class RoutingDecision(BaseModel):
    agent: str
    reasoning: str
    requires_hitl: bool
    event: InboundEvent
