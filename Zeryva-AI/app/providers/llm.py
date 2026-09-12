import logging
from agno.models.openai import OpenAIChat
from app.config.settings import settings

logger = logging.getLogger("llm")

provider = (settings.llm_provider or "").strip().lower()

logger.info(f"Initializing model for provider '{provider}': {settings.llm_model}")
model = OpenAIChat(
    id=settings.llm_model,
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    temperature=0.2,
)
