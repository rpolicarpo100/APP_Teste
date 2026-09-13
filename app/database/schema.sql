-- GOD Cerebro Core / Local AI Brain - SQLite Schema v1.0
-- Conforme spec §14 e GOD §5.8 Project Memory

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id),
    role TEXT NOT NULL, -- user, assistant, system, tool
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    objective TEXT NOT NULL,
    expected_result TEXT,
    context TEXT, -- JSON
    constraints_text TEXT,
    priority TEXT DEFAULT 'medium', -- low, medium, high, critical
    status TEXT DEFAULT 'PENDING', -- PENDING, PLANNING, WAITING_APPROVAL, READY, RUNNING, VALIDATING, NEEDS_REVIEW, BLOCKED, FAILED, COMPLETED, CANCELLED
    autonomy_level INTEGER DEFAULT 2,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    mission_id TEXT REFERENCES missions(id),
    objective TEXT NOT NULL,
    description TEXT,
    agent_id TEXT,
    required_skills TEXT, -- JSON array
    dependencies TEXT, -- JSON array of task_ids
    priority TEXT DEFAULT 'medium',
    acceptance_criteria TEXT, -- JSON
    risk TEXT DEFAULT 'low', -- low, medium, high
    required_tools TEXT, -- JSON array
    status TEXT DEFAULT 'PENDING', -- PENDING, READY, RUNNING, SUCCEEDED, FAILED, BLOCKED, CANCELLED, RETRYING
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    result_summary TEXT,
    artifacts TEXT, -- JSON
    evidence TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    specialty TEXT NOT NULL,
    skills TEXT, -- JSON array
    tools TEXT, -- JSON array
    permissions TEXT, -- JSON
    status TEXT DEFAULT 'IDLE', -- IDLE, READY, RUNNING, FAILED, DISABLED
    execution_type TEXT DEFAULT 'local', -- local, remote
    limitations TEXT, -- JSON
    contract_version TEXT DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tools (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    description TEXT,
    input_schema TEXT, -- JSON schema
    output_schema TEXT, -- JSON schema
    permissions TEXT, -- JSON
    side_effects TEXT,
    risk_level TEXT DEFAULT 'LOW', -- LOW, MEDIUM, HIGH
    status TEXT DEFAULT 'available', -- available, unavailable, disabled
    requires_approval BOOLEAN DEFAULT FALSE,
    allowed_paths TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL, -- short, long, episodic, semantic
    content TEXT NOT NULL,
    source TEXT,
    confidence TEXT DEFAULT 'medium', -- low, medium, high
    mission_id TEXT REFERENCES missions(id),
    task_id TEXT REFERENCES tasks(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS experiences (
    id TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    agent TEXT,
    action TEXT,
    result TEXT,
    error TEXT,
    lesson TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tool_calls (
    id TEXT PRIMARY KEY,
    task_id TEXT REFERENCES tasks(id),
    mission_id TEXT REFERENCES missions(id),
    tool_id TEXT REFERENCES tools(id),
    agent_id TEXT,
    input TEXT, -- JSON
    output TEXT, -- JSON
    duration_ms INTEGER,
    status TEXT, -- success, failed, blocked
    risk TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    task_id TEXT REFERENCES tasks(id),
    mission_id TEXT REFERENCES missions(id),
    agent_id TEXT,
    tool_id TEXT,
    action TEXT NOT NULL,
    target TEXT,
    risk TEXT,
    payload TEXT, -- JSON
    status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, DENIED, EXPIRED
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mission_id TEXT,
    task_id TEXT,
    agent_id TEXT,
    tool_id TEXT,
    event_type TEXT NOT NULL, -- TaskCreated, TaskStarted, ToolCalled, etc §21
    actor TEXT,
    details TEXT, -- JSON
    severity TEXT DEFAULT 'INFO'
);

CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cron_expression TEXT NOT NULL,
    agent TEXT,
    payload TEXT, -- JSON
    enabled BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS businesses (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT,
    description TEXT,
    status TEXT DEFAULT 'ativo',
    business_model TEXT,
    value_proposition TEXT,
    customer_segment TEXT,
    channel TEXT,
    revenue_monthly REAL DEFAULT 0,
    costs_monthly REAL DEFAULT 0,
    currency TEXT DEFAULT 'EUR',
    website_url TEXT,
    logo_url TEXT,
    tags TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_tasks_mission ON tasks(mission_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tool_calls_task ON tool_calls(task_id);
CREATE INDEX IF NOT EXISTS idx_audit_mission ON audit_logs(mission_id);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_businesses_status ON businesses(status);
