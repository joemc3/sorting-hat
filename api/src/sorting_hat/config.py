from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/sorting_hat"
    api_prefix: str = "/api/v1"
    debug: bool = False
    llm_provider: str = "openrouter"  # "openrouter", "openai", "ollama"
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "anthropic/claude-sonnet-4-20250514"

    model_config = {"env_prefix": "SORTING_HAT_", "env_file": ".env"}


settings = Settings()
