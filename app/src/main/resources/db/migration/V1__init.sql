-- Team members
CREATE TABLE IF NOT EXISTS team_members (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  relationship_to_manager TEXT NOT NULL,
  start_date TEXT NOT NULL
);

-- Feedback (no FK for MVP to allow AI-resolved IDs not in roster yet)
CREATE TABLE IF NOT EXISTS feedback (
  id TEXT PRIMARY KEY,
  team_member_id TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
);

