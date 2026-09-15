from pathlib import Path
from agno.agent import Agent
from app.providers.llm import model
from app.models.schemas import SkillsExtractionResponse, AgentSkill

PROMPT_DIR = Path(__file__).parent


class SkillsAgent:
    """
    Skills Extractor Agent that analyzes synthesized system prompts and business context
    to identify required knowledge search and text retrieval skills.
    """

    def __init__(self) -> None:
        system_prompt = (PROMPT_DIR / "skills_system_prompt.md").read_text(encoding="utf-8")
        self.user_template = (PROMPT_DIR / "skills_user_prompt.md").read_text(encoding="utf-8")
        self.agent = Agent(
            name="Skills Extractor Agent",
            model=model,
            description="Extracts knowledge retrieval and text search skills for the agent.",
            instructions=system_prompt,
            output_schema=SkillsExtractionResponse,
        )

    def run(
        self,
        agent_name: str,
        business_name: str,
        business_type: str,
        system_prompt_text: str,
        collected_answers: str,
    ) -> list[AgentSkill]:
        """
        Executes skills extraction for a given system prompt and business context.

        Args:
            agent_name (str): Synthesized agent name.
            business_name (str): Name of the business.
            business_type (str): Industry / type of business.
            system_prompt_text (str): Generated system prompt text.
            collected_answers (str): Formatted questionnaire answers string.

        Returns:
            list[AgentSkill]: List of extracted knowledge search skills.
        """
        prompt = self.user_template.format(
            agent_name=agent_name,
            business_name=business_name,
            business_type=business_type,
            system_prompt=system_prompt_text,
            collected_answers=collected_answers,
        )
        response = self.agent.run(prompt)
        response_data = response.content
        if isinstance(response_data, str):
            raise RuntimeError(f"Skills Agent LLM generation failed: {response_data}")
        return response_data.skills


# Singleton instance for simple imports
skills_agent = SkillsAgent()


def extract_agent_skills(
    agent_name: str,
    business_name: str,
    business_type: str,
    system_prompt_text: str,
    collected_answers: str,
) -> list[AgentSkill]:
    """Functional shortcut delegating to skills_agent instance."""
    return skills_agent.run(
        agent_name=agent_name,
        business_name=business_name,
        business_type=business_type,
        system_prompt_text=system_prompt_text,
        collected_answers=collected_answers,
    )
