import time
import pytest
from agno.agent import Agent
from app.providers.llm import model
from app.models.schemas import (
    BusinessProfileBase,
    BuilderInput,
    ProfilerSchemaResponse,
    Step1PromptResponse,
)
from app.services.agents.profiling_agent.agent import profiling_agent
from app.services.agents.builder_agent.agent import builder_agent
from app.services.agents.builder_agent.skills_agent.agent import skills_agent


@pytest.mark.llm
def test_hi_to_llm():
    """
    Smoke test: Sends a simple 'hi' prompt directly to the LLM model.
    Verifies API keys, model configuration, and basic provider reachability.
    """
    test_agent = Agent(
        name="LLM Ping Agent",
        model=model,
        description="Health check ping agent",
    )
    try:
        response = test_agent.run("Hi! Reply with 'Hello World'")
        assert response and response.content, "LLM returned empty response"
        assert len(str(response.content)) > 0, "LLM response content should not be empty"
        print(f"\n[LLM Ping Response]: {response.content}")
    except Exception as exc:
        err_msg = str(exc).lower()
        if any(k in err_msg for k in ["422", "429", "quota", "rate limit", "resource_exhausted"]):
            pytest.skip(f"LLM API rate limit or quota exceeded: {exc}")
        raise


@pytest.mark.llm
def test_profiler_agent_llm_call():
    """
    Integration test: ProfilingAgent generates dynamic onboarding fields.
    Verifies that the LLM returns a valid ProfilerSchemaResponse object with fields.
    """
    time.sleep(1)
    profile = BusinessProfileBase(
        business_name="Zeryva Tech Solutions",
        business_type="Software Consultancy",
        location="New York, NY",
        offerings=["Web App Development", "AI Integration", "Cloud Architecture"],
        working_hours="9 AM - 6 PM EST",
    )

    try:
        response = profiling_agent.run(profile)
    except Exception as exc:
        err_msg = str(exc).lower()
        if any(k in err_msg for k in ["422", "429", "quota", "rate limit", "resource_exhausted"]):
            pytest.skip(f"LLM API rate limit or quota exceeded: {exc}")
        raise

    assert isinstance(response, ProfilerSchemaResponse)
    assert len(response.fields) > 0, "Profiler agent should generate at least 1 UI question field"
    print(f"\n[Profiler Agent Output]: Generated {len(response.fields)} fields.")
    for field in response.fields:
        assert field.field_id, "Field ID must not be empty"
        assert field.question_text, "Question text must not be empty"
        assert field.ui_type, "UI type must not be empty"


@pytest.mark.llm
def test_builder_agent_llm_call():
    """
    Integration test: BuilderAgent synthesizes WhatsApp AI Agent System Prompts.
    Verifies system prompt, greeting message, and skills returned.
    """
    time.sleep(2)
    profile = BusinessProfileBase(
        business_name="Acme Logistics",
        business_type="Freight & Shipping",
        location="Chicago, IL",
        offerings=["Package Tracking", "Rate Calculator", "Customer Support"],
    )
    builder_input = BuilderInput(business_profile=profile)

    try:
        step1_data, skills = builder_agent.run(builder_input)
    except Exception as exc:
        err_msg = str(exc).lower()
        if any(k in err_msg for k in ["422", "429", "quota", "rate limit", "resource_exhausted"]):
            pytest.skip(f"LLM API rate limit or quota exceeded: {exc}")
        raise

    assert isinstance(step1_data, Step1PromptResponse)
    assert step1_data.agent_name, "Generated agent name must not be empty"
    assert len(step1_data.system_prompt) > 50, "System prompt should contain full agent instructions"
    assert step1_data.greeting_message, "Greeting message must not be empty"
    assert isinstance(skills, list)
    print(f"\n[Builder Agent Output]: Synthesized agent '{step1_data.agent_name}'.")


@pytest.mark.llm
def test_skills_agent_llm_call():
    """
    Integration test: SkillsAgent extracts required knowledge search skills.
    Verifies extracted skills list.
    """
    time.sleep(2)
    try:
        skills = skills_agent.run(
            agent_name="Acme Support Bot",
            business_name="Acme Logistics",
            business_type="Freight & Shipping",
            system_prompt_text="You are Acme Support Bot. Search order database and track packages.",
            collected_answers="- **Tracking**: Customer needs real-time shipment updates",
        )
    except Exception as exc:
        err_msg = str(exc).lower()
        if any(k in err_msg for k in ["422", "429", "quota", "rate limit", "resource_exhausted"]):
            pytest.skip(f"LLM API rate limit or quota exceeded: {exc}")
        raise

    assert isinstance(skills, list)
    print(f"\n[Skills Agent Output]: Extracted {len(skills)} skills.")
