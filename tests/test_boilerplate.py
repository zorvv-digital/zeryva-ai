import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.db.session import Base
from app.models.schemas import HealthResponse

def test_settings_initialization():
    assert settings.PROJECT_NAME is not None
    assert settings.API_V1_STR == "/api/v1"


def test_schema_instantiation():
    health = HealthResponse(status="online", app_name="TestApp", version="0.1.0")
    assert health.status == "online"

if __name__ == "__main__":
    test_settings_initialization()
    test_schema_instantiation()
    print("✅ All generic boilerplate tests passed successfully!")
