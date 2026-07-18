from app.db import jira_client as jira
from app.config import settings

PROJECT = settings.jira_project_key


def get_sprint_health() -> dict:
    """
    Returns a health summary for the active sprint:
    total tickets, by status, blocked count, completion percentage.
    """
    sp_field = jira.get_story_points_field()
    data = jira.get("/search", {
        "jql": f"project = {PROJECT} AND sprint in openSprints()",
        "fields": f"summary,status,assignee,priority,labels,{sp_field}",
        "maxResults": 100,
    })

    issues = data.get("issues", [])
    status_counts: dict[str, int] = {}
    blocked = 0
    total_points = 0
    completed_points = 0

    for issue in issues:
        fields = issue["fields"]
        status = fields["status"]["name"]
        status_counts[status] = status_counts.get(status, 0) + 1

        labels = fields.get("labels", [])
        if "blocked" in [l.lower() for l in labels]:
            blocked += 1

        points = fields.get(sp_field) or 0
        total_points += points
        if status.lower() == "done":
            completed_points += points

    completion_pct = round((completed_points / total_points * 100), 1) if total_points else 0

    return {
        "total_tickets": len(issues),
        "by_status": status_counts,
        "blocked_count": blocked,
        "total_story_points": total_points,
        "completed_story_points": completed_points,
        "completion_percentage": completion_pct,
    }


def get_blocked_tickets() -> list[dict]:
    """
    Returns all tickets in the active sprint that are labelled 'blocked'
    or have 'blocked' in their status, with assignee and age in days.
    """
    data = jira.get("/search", {
        "jql": (
            f"project = {PROJECT} AND sprint in openSprints() "
            f"AND (labels = blocked OR status = Blocked)"
        ),
        "fields": "summary,status,assignee,priority,created,updated",
        "maxResults": 50,
    })

    results = []
    for issue in data.get("issues", []):
        fields = issue["fields"]
        results.append({
            "ticket_id": issue["key"],
            "title": fields["summary"],
            "status": fields["status"]["name"],
            "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
            "priority": fields["priority"]["name"],
            "updated": fields["updated"],
        })
    return results


def get_ungroomed_stories() -> list[dict]:
    """
    Returns tickets in the active sprint that are missing story points,
    assignee, or description — the three grooming essentials.
    """
    sp_field = jira.get_story_points_field()
    data = jira.get("/search", {
        "jql": (
            f"project = {PROJECT} AND sprint in openSprints() "
            f"AND issueType != Sub-task"
        ),
        "fields": f"summary,status,assignee,description,{sp_field}",
        "maxResults": 100,
    })

    ungroomed = []
    for issue in data.get("issues", []):
        fields = issue["fields"]
        missing = []

        if not fields.get(sp_field):
            missing.append("story points")
        if not fields.get("assignee"):
            missing.append("assignee")
        if not fields.get("description"):
            missing.append("description")

        if missing:
            ungroomed.append({
                "ticket_id": issue["key"],
                "title": fields["summary"],
                "status": fields["status"]["name"],
                "missing_fields": missing,
            })

    return ungroomed


def get_team_velocity(num_sprints: int = 4) -> list[dict]:
    """
    Returns story points completed per sprint for the last N sprints.
    Provides the data behind the north star metric.
    """
    sp_field = jira.get_story_points_field()
    board_data = jira.get("/rest/agile/1.0/board", {"projectKeyOrId": PROJECT})

    # Use first board found for this project
    boards = board_data.get("values", [])
    if not boards:
        return []
    board_id = boards[0]["id"]

    sprints_data = jira.get(
        f"/rest/agile/1.0/board/{board_id}/sprint",
        {"state": "closed", "maxResults": num_sprints}
    )

    velocity = []
    for sprint in sprints_data.get("values", [])[-num_sprints:]:
        sprint_id = sprint["id"]
        issues = jira.get("/search", {
            "jql": f"project = {PROJECT} AND sprint = {sprint_id} AND status = Done",
            "fields": sp_field,
            "maxResults": 100,
        })
        points = sum(
            (i["fields"].get(sp_field) or 0)
            for i in issues.get("issues", [])
        )
        velocity.append({
            "sprint_name": sprint["name"],
            "completed_points": points,
            "start_date": sprint.get("startDate"),
            "end_date": sprint.get("endDate"),
        })

    return velocity


def get_ticket_detail(ticket_id: str) -> dict:
    """
    Returns full detail for a single ticket: summary, description,
    acceptance criteria, comments, status, assignee, story points.
    """
    sp_field = jira.get_story_points_field()
    data = jira.get(f"/issue/{ticket_id}", {
        "fields": f"summary,description,status,assignee,priority,labels,{sp_field},comment,parent"
    })

    fields = data["fields"]
    comments = [
        {
            "author": c["author"]["displayName"],
            "body": c["body"],
            "created": c["created"],
        }
        for c in (fields.get("comment") or {}).get("comments", [])
    ]

    return {
        "ticket_id": data["key"],
        "title": fields["summary"],
        "status": fields["status"]["name"],
        "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
        "priority": fields["priority"]["name"],
        "story_points": fields.get(sp_field),
        "labels": fields.get("labels", []),
        "description": fields.get("description"),
        "parent": (fields.get("parent") or {}).get("key"),
        "comments": comments,
    }


def jql_search(jql: str, max_results: int = 50) -> list[dict]:
    """
    Fallback: executes a raw JQL query for freeform SM questions
    that don't map to a pre-built tool. Used by Ticket Agent only
    after pre-built tools are exhausted.
    """
    sp_field = jira.get_story_points_field()
    data = jira.get("/search", {
        "jql": jql,
        "fields": f"summary,status,assignee,priority,{sp_field}",
        "maxResults": max_results,
    })
    return [
        {
            "ticket_id": i["key"],
            "title": i["fields"]["summary"],
            "status": i["fields"]["status"]["name"],
            "assignee": (i["fields"].get("assignee") or {}).get("displayName", "Unassigned"),
            "story_points": i["fields"].get(sp_field),
        }
        for i in data.get("issues", [])
    ]
