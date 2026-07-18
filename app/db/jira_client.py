import httpx
import base64
from typing import Optional
from app.config import settings

# Basic Auth header — email:api_token base64-encoded, required by JIRA Cloud
_credentials = base64.b64encode(
    f"{settings.jira_email}:{settings.jira_api_token}".encode()
).decode()

HEADERS = {
    "Authorization": f"Basic {_credentials}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

BASE_URL = settings.jira_base_url.rstrip("/")

# Cached in memory after first discovery — avoids repeated /field calls
_story_points_field: Optional[str] = None


def get(path: str, params: dict = None) -> dict:
    """
    GET request to JIRA REST API.
    Paths starting with /rest/ are used as-is (e.g. Agile API).
    All other paths are prefixed with /rest/api/3.
    """
    if path.startswith("/rest/"):
        url = f"{BASE_URL}{path}"
    else:
        url = f"{BASE_URL}/rest/api/3{path}"
    response = httpx.get(url, headers=HEADERS, params=params or {})
    response.raise_for_status()
    return response.json()


def post(path: str, body: dict) -> dict:
    """POST request to JIRA REST API v3."""
    url = f"{BASE_URL}/rest/api/3{path}"
    response = httpx.post(url, headers=HEADERS, json=body)
    response.raise_for_status()
    return response.json()


def put(path: str, body: dict) -> dict:
    """PUT request to JIRA REST API v3."""
    url = f"{BASE_URL}/rest/api/3{path}"
    response = httpx.put(url, headers=HEADERS, json=body)
    response.raise_for_status()
    return response.json()


def get_story_points_field() -> str:
    """
    Discovers the Story Points custom field ID for this JIRA instance.
    JIRA Cloud stores story points as customfield_XXXXX — the ID varies
    per instance. We fetch all fields once and cache the result.
    """
    global _story_points_field
    if _story_points_field:
        return _story_points_field

    fields = get("/field")
    for field in fields:
        if field.get("name", "").lower() in ("story points", "story point estimate"):
            _story_points_field = field["id"]
            return _story_points_field

    # Fallback to most common JIRA Cloud field IDs if discovery fails
    _story_points_field = "customfield_10016"
    return _story_points_field
