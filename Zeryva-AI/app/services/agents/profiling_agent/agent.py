from pathlib import Path
from agno.agent import Agent
from app.providers.llm import model
from app.models.schemas import BusinessProfileBase, ProfilerSchemaResponse

PROMPT_DIR = Path(__file__).parent


class ProfilingAgent:
    """
    Dynamic Profiling Agent that generates customized onboarding questionnaires
    based on a business profile.
    """

    def __init__(self) -> None:
        system_prompt = (PROMPT_DIR / "profiler_system_prompt.md").read_text(encoding="utf-8")
        self.user_template = (PROMPT_DIR / "profiler_user_prompt.md").read_text(encoding="utf-8")
        self.agent = Agent(
            name="Profiling Agent",
            model=model,
            description="Analyzes business profiles and generates dynamic UI schemas for onboarding.",
            instructions=system_prompt,
            output_schema=ProfilerSchemaResponse,
        )

    def run(self, profile: BusinessProfileBase) -> ProfilerSchemaResponse:
        """
        Executes the profiling agent to produce dynamic questionnaire fields.

        Args:
            profile (BusinessProfileBase): Business profile details.

        Returns:
            ProfilerSchemaResponse: Generated UI questionnaire fields.
        """
        prompt = self.user_template.format(
            business_name=profile.business_name,
            business_type=profile.business_type,
            location=profile.location or "Not specified",
            offerings=", ".join(profile.offerings) if profile.offerings else "Not specified",
            working_hours=profile.working_hours or "Not specified",
        )
        response = self.agent.run(prompt)
        if isinstance(response.content, str):
            raise RuntimeError(f"Profiling Agent LLM generation failed: {response.content}")
        return response.content


# Singleton instance for simple service imports
profiling_agent = ProfilingAgent()


def generate_profiling_schema(profile: BusinessProfileBase) -> ProfilerSchemaResponse:
    """Functional shortcut delegating to profiling_agent instance."""
    return profiling_agent.run(profile)
