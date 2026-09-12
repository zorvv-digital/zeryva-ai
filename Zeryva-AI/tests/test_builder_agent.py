import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.models.schemas import BuilderInput, BusinessProfileBase, AgentSetup, BuilderAgentResponse

client = TestClient(app)

def test_builder_schemas():
    profile = BusinessProfileBase(
        business_name="Test Cafe",
        business_type="Restaurant",
        offerings=["Coffee", "Pastries"]
    )
    setup = AgentSetup(
        agent_name="Cafe Assistant",
        personality="Friendly and warm",
        business_objective="Help customers with menu choices",
        rules=["Never offer unauthorized discounts"]
    )
    builder_input = BuilderInput(
        business_profile=profile,
        collected_answers={"delivery": "Available via DoorDash"},
        agent_setup=setup
    )
    assert builder_input.business_profile.business_name == "Test Cafe"
    assert builder_input.agent_setup.agent_name == "Cafe Assistant"

def test_openapi_schema_contains_projects_and_builder_routes():
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json().get("paths", {})
    assert "/api/v1/builder/generate-agent" in paths
    assert "/api/v1/projects" in paths
    assert "/api/v1/projects/{project_id}/agents" in paths
    assert "/api/v1/agents/{agent_id}" in paths
