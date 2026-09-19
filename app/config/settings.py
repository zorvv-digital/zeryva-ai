from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices, model_validator
from typing import Optional
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "Zeryva AI Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Generic LLM configuration
    llm_provider: str = "gemini"  # 'nim', 'openai', 'gemini', 'anthropic', etc.
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None

    # Provider-specific configurations
    nim_api_key: Optional[str] = None
    nim_model: Optional[str] = None
    nim_base_url: Optional[str] = None

    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    gemini_base_url: Optional[str] = None

    @model_validator(mode="after")
    def resolve_llm_config(self) -> 'Settings':
        provider = (self.llm_provider or "").strip().lower()
        if provider == "nim":
            if self.nim_api_key:
                self.llm_api_key = self.nim_api_key
            if self.nim_model:
                self.llm_model = self.nim_model
            if self.nim_base_url:
                self.llm_base_url = self.nim_base_url
        elif provider == "gemini":
            if self.gemini_api_key:
                self.llm_api_key = self.gemini_api_key
            if self.gemini_model:
                self.llm_model = self.gemini_model
            if self.gemini_base_url:
                self.llm_base_url = self.gemini_base_url
        return self

    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./zeryva_ai.db"

    # Security
    SECRET_KEY: str = "zeryva-super-secret-key-change-in-production-32bytes!"

    # WhatsApp configuration
    whatsapp_verify_token: Optional[str] = None
    whatsapp_token: Optional[str] = Field(None, validation_alias=AliasChoices("whatsapp_token", "whatsapp_access_token"))
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_api_version: str = "v20.0"


settings = Settings()
