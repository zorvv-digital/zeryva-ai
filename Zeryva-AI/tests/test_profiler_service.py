"""
Unit tests for ProfilerService and Profiling Agent placeholder formatting.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import ProfilerService
from app.models.schemas import (
    BusinessProfileBase,
    ProfilerSchemaResponse,
    DynamicUIField,
)


def test_profiler_service_generates_schema():
    """Verify ProfilerService delegates to generate_profiling_schema correctly."""
    profile = BusinessProfileBase(
        business_name="Acme Dental",
        business_type="Healthcare",
        location="New York",
        offerings=["Teeth Cleaning", "Whitening"],
        working_hours="9 AM - 5 PM",
    )

    expected_response = ProfilerSchemaResponse(
        fields=[
            DynamicUIField(
                field_id="insurance",
                question_text="Do you accept insurance?",
                ui_type="radio",
                options=["Yes", "No"],
                is_required=True,
            )
        ]
    )

    with patch("app.services.agents.profiling_agent.agent.profiling_agent.agent.run") as mock_run:
        mock_run.return_value = MagicMock(content=expected_response)

        result = ProfilerService.generate_questions(profile)

        # Assert response schema returned matches expected output
        assert len(result.fields) == 1
        assert result.fields[0].field_id == "insurance"

        # Assert profile attributes were interpolated into prompt placeholders
        prompt_passed = mock_run.call_args[0][0]
        assert "Acme Dental" in prompt_passed
        assert "Healthcare" in prompt_passed
        assert "New York" in prompt_passed
        assert "Teeth Cleaning, Whitening" in prompt_passed
        assert "9 AM - 5 PM" in prompt_passed
