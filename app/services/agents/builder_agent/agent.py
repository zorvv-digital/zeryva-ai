from pathlib import Path
from agno.agent import Agent
from app.providers.llm import model
from app.models.schemas import BuilderInput, Step1PromptResponse, AgentSkill
from app.services.agents.builder_agent.skills_agent.agent import skills_agent

PROMPT_DIR = Path(__file__).parent


class BuilderAgent:
    """
    Builder Agent responsible for synthesizing production AI agent system prompts
    and orchestrating knowledge search skill extraction.
    """

    def __init__(self) -> None:
        system_prompt = (PROMPT_DIR / "builder_system_prompt.md").read_text(encoding="utf-8")
        self.user_template = (PROMPT_DIR / "builder_user_prompt.md").read_text(encoding="utf-8")
        self.agent = Agent(
            name="Builder Agent",
            model=model,
            description="Synthesizes business profiling and onboarding data into a WhatsApp AI agent system prompt.",
            instructions=system_prompt,
            output_schema=Step1PromptResponse,
        )

    def run(self, builder_input: BuilderInput) -> tuple[Step1PromptResponse, list[AgentSkill]]:
        """
        Executes the Builder Agent pipeline:
        1. Formats input profile and setup preferences into user prompt placeholders.
        2. Executes Step 1 Builder Agent to synthesize prompt & greeting message.
        3. Conditionally delegates Step 2 to SkillsAgent if knowledge search is required.

        Args:
            builder_input (BuilderInput): Incoming builder configuration payload.

        Returns:
            tuple[Step1PromptResponse, list[AgentSkill]]: Synthesized prompt response and list of extracted skills.
        """
        profile = builder_input.business_profile
        setup = builder_input.agent_setup

        # Format questionnaire answers string
        formatted_answers = (
            "\n".join(f"- **{k}**: {v}" for k, v in builder_input.collected_answers.items())
            if builder_input.collected_answers
            else "No additional questionnaire answers provided."
        )

        # Format custom rules string
        formatted_rules = (
            "\n".join(f"- {r}" for r in setup.rules)
            if (setup and setup.rules)
            else "- Standard customer service rules apply."
        )

        # Interpolate prompt placeholders
        prompt = self.user_template.format(
            business_name=profile.business_name,
            business_type=profile.business_type,
            location=profile.location or "Not specified",
            working_hours=profile.working_hours or "Not specified",
            offerings=", ".join(profile.offerings) if profile.offerings else "Not specified",
            collected_answers=formatted_answers,
            agent_name=setup.agent_name if (setup and setup.agent_name) else "Default Assistant",
            personality=setup.personality if (setup and setup.personality) else "Professional, friendly, and helpful",
            business_objective=setup.business_objective if (setup and setup.business_objective) else "Assist customers with inquiries and general support",
            custom_rules=formatted_rules,
        )

        # Step 1: Synthesize prompt & greeting message
        response = self.agent.run(prompt)
        step1_data = response.content
        if isinstance(step1_data, str):
            raise RuntimeError(f"Builder Agent LLM generation failed: {step1_data}")

        # Step 2: Conditionally extract knowledge search skills
        skills: list[AgentSkill] = []
        if step1_data.requires_knowledge_search:
            skills = skills_agent.run(
                agent_name=step1_data.agent_name,
                business_name=profile.business_name,
                business_type=profile.business_type,
                system_prompt_text=step1_data.system_prompt,
                collected_answers=formatted_answers,
            )

        return step1_data, skills


# Singleton instance for simple imports
builder_agent = BuilderAgent()


def synthesize_agent_config(
    builder_input: BuilderInput,
) -> tuple[Step1PromptResponse, list[AgentSkill]]:
    """Functional shortcut delegating to builder_agent instance."""
    return builder_agent.run(builder_input)
