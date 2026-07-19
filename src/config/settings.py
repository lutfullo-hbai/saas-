from pathlib import Path

from pydantic_settings import BaseSettings


def _read_secret(filename: str, default: str = "") -> str:
    """Docker secrets faylini o'qish (production uchun)."""
    secret_path = Path(f"/run/secrets/{filename}")
    if secret_path.exists():
        return secret_path.read_text().strip()
    return default


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # PostgreSQL
    database_url: str = (
        "postgresql+asyncpg://disipl:changeme@localhost:5432/discipline_db"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Telegram Bot
    telegram_bot_token: str = ""

    # JWT
    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    jwt_refresh_secret_key: str = "changeme-refresh"
    jwt_refresh_expiration_days: int = 30

    # LLM
    llm_provider: str = "claude"
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Payment — Payme
    payme_merchant_id: str = ""
    payme_secret_key: str = ""

    # Payment — Click
    click_merchant_id: str = ""
    click_secret_key: str = ""

    # Payment default provider
    payment_provider: str = "payme"  # "payme" yoki "click"

    # Encryption
    encryption_key: str = ""

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    secret_env_mode: str = "development"  # "development" yoki "production"
    cors_origins: str = "http://localhost:3000,http://localhost:5173,https://disipl.uz"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS origins ni list formatda qaytarish."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def model_post_init(self, __context) -> None:
        """Production mode'da Docker secrets'dan secretlarni o'qish."""
        if self.secret_env_mode == "production":
            self.jwt_secret_key = _read_secret("jwt_secret", self.jwt_secret_key)
            self.jwt_refresh_secret_key = _read_secret(
                "jwt_refresh_secret", self.jwt_refresh_secret_key
            )
            db_pass = _read_secret("db_password")
            if db_pass and "changeme" in self.database_url:
                self.database_url = self.database_url.replace("changeme", db_pass)


settings = Settings()
