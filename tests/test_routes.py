"""
Integration tests for FastAPI router registrations and OpenAPI documentation.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify system health check route returns OK."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema_contains_all_registered_routes():
    """Verify that project, agent, tool, profiler, and system endpoints are present in OpenAPI spec."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    paths = spec.get("paths", {})

    expected_routes = [
        "/api/v1/projects",
        "/api/v1/projects/{project_id}/agents",
        "/api/v1/projects/{project_id}/chat",
        "/api/v1/projects/{project_id}/agents/{agent_id}/tools",
        "/api/v1/projects/{project_id}/agents/{agent_id}/tools/{tool_id}",
        "/api/v1/agents/{agent_id}",
        "/api/v1/agents/builder/generate",
        "/api/v1/profiler/generate-questions",
        "/api/v1/health",
    ]

    for route in expected_routes:
        assert route in paths, f"Expected route {route} not found in OpenAPI spec"

    # Verify deprecated builder route is NOT present
    assert "/api/v1/builder/generate-agent" not in paths, "Deprecated route /api/v1/builder/generate-agent still present in OpenAPI spec"

    # Verify health route is tagged under System (no default tag group)
    health_tags = paths["/api/v1/health"]["get"].get("tags", [])
    assert health_tags == ["System"], f"Expected health tags to be ['System'], got {health_tags}"
