from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBHOOK_URL: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:ziyrak2026@localhost:5432/ziyrak_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    SENTRY_DSN: str = ""
    PAYME_MERCHANT_ID: str = ""
    CLICK_MERCHANT_ID: str = ""
    APP_ENV: str = "development"
    SECRET_KEY: str = "ziyrak-secret-key-2026"
    ADMIN_IDS: str = ""

    @property
    def admin_ids_list(self) -> List[int]:
        return [int(x) for x in self.ADMIN_IDS.split(",") if x.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()