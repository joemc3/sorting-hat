from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/sorting_hat"
    api_prefix: str = "/api/v1"
    debug: bool = False

    model_config = {"env_prefix": "SORTING_HAT_", "env_file": ".env"}


settings = Settings()
