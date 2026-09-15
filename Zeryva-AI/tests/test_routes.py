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
    """Verify that all project, agent, profiler, and builder endpoints are present in OpenAPI spec."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json().get("paths", {})

    expected_routes = [
        "/api/v1/projects",
        "/api/v1/projects/{project_id}/agents",
        "/api/v1/agents/{agent_id}",
        "/api/v1/agents/builder/generate",
        "/api/v1/builder/generate-agent",
        "/api/v1/profiler/generate-questions",
        "/api/v1/health",
    ]

    for route in expected_routes:
        assert route in paths, f"Expected route {route} not found in OpenAPI spec"
