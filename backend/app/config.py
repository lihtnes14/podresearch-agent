import os
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class Settings:
    # OpenAI / Azure OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY") or ""
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL") or os.getenv("AZURE_OPENAI_ENDPOINT")
    MODEL_NAME: str = (
        os.getenv("AZURE_OPENAI_DEPLOYMENT")
        or os.getenv("OPENAI_MODEL_NAME")
        or "gpt-4o"
    )

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]

    # Pipeline Settings
    DEFAULT_CHUNK_DURATION: int = int(os.getenv("DEFAULT_CHUNK_DURATION", "300"))
    TIMEOUT_SECONDS: int = int(os.getenv("DEFAULT_TIMEOUT_SECONDS", "45"))
    MAX_RETRIES: int = 1

    # Medium & Dev.to Publishing Integration
    MEDIUM_INTEGRATION_TOKEN: Optional[str] = os.getenv("MEDIUM_INTEGRATION_TOKEN")
    DEVTO_API_KEY: Optional[str] = os.getenv("DEVTO_API_KEY")


settings = Settings()


def get_llm(temperature: float = 0.1) -> ChatOpenAI:
    """Returns a configured LangChain ChatOpenAI client with timeout protection."""
    return ChatOpenAI(
        model=settings.MODEL_NAME,
        openai_api_base=settings.OPENAI_BASE_URL,
        openai_api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
        timeout=settings.TIMEOUT_SECONDS,
        max_retries=settings.MAX_RETRIES,
    )
