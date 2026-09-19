"""
Unit tests for Builder Agent synthesis pipeline and placeholder interpolation.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.schemas import (
    BuilderInput,
    BusinessProfileBase,
    AgentSetup,
    Step1PromptResponse,
    AgentSkill,
    SkillsExtractionResponse,
)
from app.services.agents.builder_agent.agent import synthesize_agent_config


def test_builder_agent_prompt_placeholder_interpolation():
    """Verify Builder Agent populates prompt placeholders and conditionally extracts skills."""
    builder_input = BuilderInput(
        business_profile=BusinessProfileBase(
            business_name="Cafe Delight",
            business_type="Restaurant",
            location="Chicago",
            offerings=["Espresso", "Croissant"],
            working_hours="7 AM - 6 PM",
        ),
        collected_answers={"delivery_app": "UberEats"},
        agent_setup=AgentSetup(
            agent_name="Delight Bot",
            personality="Energetic and polite",
            business_objective="Take orders and answer questions",
            rules=["Always greet with smile emoji"],
        ),
    )

    with patch("app.services.agents.builder_agent.agent.builder_agent.agent.run") as mock_step1, \
         patch("app.services.agents.builder_agent.skills_agent.agent.skills_agent.agent.run") as mock_step2:

        # Mock LLM Step 1 response (flags that knowledge search is required)
        mock_step1.return_value = MagicMock(
            content=Step1PromptResponse(
                agent_name="Delight Bot",
                system_prompt="You are Delight Bot...",
                greeting_message="Hi from Cafe Delight!",
                requires_knowledge_search=True,
            )
        )
        # Mock LLM Step 2 response (returns extracted skill)
        mock_step2.return_value = MagicMock(
            content=SkillsExtractionResponse(
                skills=[
                    AgentSkill(
                        skill_name="menu_text_search",
                        description="Searches menu items",
                        is_required=True,
                    )
                ]
            )
        )

        step1_data, skills = synthesize_agent_config(builder_input)

        # Assert Step 1 outputs
        assert step1_data.agent_name == "Delight Bot"
        assert step1_data.greeting_message == "Hi from Cafe Delight!"
        assert len(skills) == 1
        assert skills[0].skill_name == "menu_text_search"

        # Verify Step 1 user prompt contained interpolated placeholders
        step1_prompt = mock_step1.call_args[0][0]
        assert "Cafe Delight" in step1_prompt
        assert "Restaurant" in step1_prompt
        assert "Chicago" in step1_prompt
        assert "UberEats" in step1_prompt
        assert "Delight Bot" in step1_prompt
        assert "Energetic and polite" in step1_prompt

        # Verify Step 2 skills prompt contained interpolated placeholders
        step2_prompt = mock_step2.call_args[0][0]
        assert "Delight Bot" in step2_prompt
        assert "Cafe Delight" in step2_prompt
