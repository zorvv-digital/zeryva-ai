from app.services.base import BaseService
from app.models.schemas import BusinessProfileBase, ProfilerSchemaResponse
from app.services.agents.profiling_agent.agent import generate_profiling_schema


class ProfilerService(BaseService):
    """
    Service layer handling onboarding business questionnaire profiling.
    """

    @classmethod
    def generate_questions(cls, profile: BusinessProfileBase) -> ProfilerSchemaResponse:
        """
        Delegates business profile data to the Dynamic Profiling Agent to generate a customized
        onboarding questionnaire UI schema.

        Args:
            profile (BusinessProfileBase): Input business profile payload containing name, type, offerings, etc.

        Returns:
            ProfilerSchemaResponse: Generated dynamic UI fields and question schema.
        """
        return generate_profiling_schema(profile)
