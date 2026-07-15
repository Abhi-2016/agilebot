-- AgileBot MVP Schema

CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    jira_project_key TEXT NOT NULL,
    teams_channel_id TEXT,
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    teams_id TEXT,
    jira_id TEXT,
    role TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    goal TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'active',
    committed_points INT DEFAULT 0,
    completed_points INT DEFAULT 0,
    velocity INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- source: where the blocker was detected (teams, jira, standup, email)
-- status: open, in_progress, resolved, escalated
CREATE TABLE blockers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sprint_id UUID REFERENCES sprints(id) ON DELETE CASCADE,
    reporter_id UUID REFERENCES members(id),
    source TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    resolution_summary TEXT,
    root_cause TEXT,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    time_to_resolve_hrs NUMERIC
);

-- type: standup, planning, retro, review, grooming
CREATE TABLE ceremonies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sprint_id UUID REFERENCES sprints(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    scheduled_at TIMESTAMPTZ,
    conducted_at TIMESTAMPTZ,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- recurring_count: increments when the same action item appears across multiple retros
CREATE TABLE action_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ceremony_id UUID REFERENCES ceremonies(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES members(id),
    text TEXT NOT NULL,
    due_date DATE,
    status TEXT DEFAULT 'open',
    recurring_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
