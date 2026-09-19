import json
import sqlite3
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "zeryva_ai.db"
SEED_PATH = BASE_DIR / "db_seed.json"


def ensure_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()
    # Check if image_url column exists in projects
    cursor.execute("PRAGMA table_info(projects)")
    columns = [col[1] for col in cursor.fetchall()]
    if "image_url" not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN image_url VARCHAR(1024)")
        conn.commit()


def export_seed(db_file: Path = DB_PATH, seed_file: Path = SEED_PATH) -> dict:
    """Exports all Projects, Agents, and Tools from SQLite database into JSON seed format."""
    if not db_file.exists():
        print(f"Database file {db_file} does not exist.")
        return {}

    conn = sqlite3.connect(db_file)
    ensure_schema(conn)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch projects
    cursor.execute("SELECT id, name, description, image_url, created_at, updated_at FROM projects")
    projects = [dict(row) for row in cursor.fetchall()]

    # Fetch agents
    cursor.execute("SELECT id, project_id, agent_name, system_prompt, greeting_message, skills, is_active, created_at, updated_at FROM agents")
    agents = []
    for row in cursor.fetchall():
        d = dict(row)
        if isinstance(d.get("skills"), str):
            try:
                d["skills"] = json.loads(d["skills"])
            except Exception:
                pass
        agents.append(d)

    # Fetch tools
    cursor.execute("SELECT id, project_id, agent_id, name, description, tool_type, config, is_active, created_at, updated_at FROM tools")
    tools = []
    for row in cursor.fetchall():
        d = dict(row)
        if isinstance(d.get("config"), str):
            try:
                d["config"] = json.loads(d["config"])
            except Exception:
                pass
        tools.append(d)

    conn.close()

    seed_data = {
        "projects": projects,
        "agents": agents,
        "tools": tools,
    }

    seed_file.write_text(json.dumps(seed_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exported {len(projects)} projects, {len(agents)} agents, {len(tools)} tools to {seed_file}")
    return seed_data


def import_seed(seed_file: Path = SEED_PATH, db_file: Path = DB_PATH) -> None:
    """Imports seed JSON into SQLite database (creating tables if necessary)."""
    if not seed_file.exists():
        print(f"Seed file {seed_file} does not exist.")
        return

    seed_data = json.loads(seed_file.read_text(encoding="utf-8"))
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create tables if not present
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        image_url VARCHAR(1024),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id VARCHAR(36) PRIMARY KEY,
        project_id VARCHAR(36) NOT NULL,
        agent_name VARCHAR(255) NOT NULL,
        system_prompt TEXT NOT NULL,
        greeting_message TEXT NOT NULL,
        skills JSON,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tools (
        id VARCHAR(36) PRIMARY KEY,
        project_id VARCHAR(36) NOT NULL,
        agent_id VARCHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        tool_type VARCHAR(50) NOT NULL DEFAULT 'text_context',
        config JSON NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
        FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
    )
    """)

    ensure_schema(conn)

    for p in seed_data.get("projects", []):
        cursor.execute(
            "INSERT OR REPLACE INTO projects (id, name, description, image_url, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (p["id"], p["name"], p.get("description"), p.get("image_url"), p.get("created_at"), p.get("updated_at"))
        )

    for a in seed_data.get("agents", []):
        skills_json = json.dumps(a["skills"]) if isinstance(a.get("skills"), (list, dict)) else a.get("skills")
        cursor.execute(
            "INSERT OR REPLACE INTO agents (id, project_id, agent_name, system_prompt, greeting_message, skills, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (a["id"], a["project_id"], a["agent_name"], a["system_prompt"], a["greeting_message"], skills_json, a.get("is_active", 1), a.get("created_at"), a.get("updated_at"))
        )

    for t in seed_data.get("tools", []):
        config_json = json.dumps(t["config"]) if isinstance(t.get("config"), (list, dict)) else t.get("config")
        cursor.execute(
            "INSERT OR REPLACE INTO tools (id, project_id, agent_id, name, description, tool_type, config, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (t["id"], t["project_id"], t["agent_id"], t["name"], t["description"], t["tool_type"], config_json, t.get("is_active", 1), t.get("created_at"), t.get("updated_at"))
        )

    conn.commit()
    conn.close()
    print(f"Imported seed data into {db_file} successfully.")


if __name__ == "__main__":
    export_seed()
