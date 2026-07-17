from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://disipl:changeme@localhost:5432/discipline_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Telegram Bot
    telegram_bot_token: str = ""

    # JWT
    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    # LLM
    llm_provider: str = "claude"
    anthropic_api_key: str = ""

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
