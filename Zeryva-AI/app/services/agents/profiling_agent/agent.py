from pathlib import Path
from agno.agent import Agent
from app.providers.llm import model
from app.models.schemas import ProfilerSchemaResponse

prompt_path = Path(__file__).parent / "prompt.md"
system_prompt = prompt_path.read_text(encoding="utf-8")

profiling_agent = Agent(
    name="Profiling Agent",
    model=model,
    description="Analyzes business profiles and generates dynamic UI schemas for onboarding.",
    instructions=system_prompt,
    output_schema=ProfilerSchemaResponse,
)

def generate_profiling_schema(business_profile_json: str) -> ProfilerSchemaResponse:
    response = profiling_agent.run(business_profile_json)
    return response.content
