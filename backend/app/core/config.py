from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, EmailStr, field_validator
from typing import List, Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CA Assists"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "change-me-before-deploying-use-secrets-token-urlsafe-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    INVITE_TOKEN_EXPIRE_HOURS: int = 48
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 30
    PASSWORD_MIN_LENGTH: int = 8

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ca_assists"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/ca_assists"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "CA Assists"
    SMTP_FROM_EMAIL: str = "noreply@caassists.com"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_BASIC_MONTHLY: str = ""
    STRIPE_PRICE_BASIC_YEARLY: str = ""
    STRIPE_PRICE_PRO_MONTHLY: str = ""
    STRIPE_PRICE_PRO_YEARLY: str = ""
    STRIPE_PRICE_ENT_MONTHLY: str = ""
    STRIPE_PRICE_ENT_YEARLY: str = ""

    @property
    def stripe_price_map(self) -> dict:
        return {
            "BASIC":  {"MONTHLY": self.STRIPE_PRICE_BASIC_MONTHLY, "YEARLY": self.STRIPE_PRICE_BASIC_YEARLY},
            "PRO":    {"MONTHLY": self.STRIPE_PRICE_PRO_MONTHLY,   "YEARLY": self.STRIPE_PRICE_PRO_YEARLY},
            "ENT":    {"MONTHLY": self.STRIPE_PRICE_ENT_MONTHLY,   "YEARLY": self.STRIPE_PRICE_ENT_YEARLY},
        }

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
