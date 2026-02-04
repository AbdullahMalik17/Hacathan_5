"""
Configuration management using Pydantic Settings.
Loads all environment variables for the application.

Task: T020 - Implement configuration management loading all environment variables
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / "backend" / ".env"

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/customer_success",
        description="PostgreSQL connection URL with asyncpg driver"
    )
    DB_POOL_MIN_SIZE: int = Field(default=10, ge=1, le=100)
    DB_POOL_MAX_SIZE: int = Field(default=20, ge=1, le=100)
    DB_QUERY_TIMEOUT: int = Field(default=30, ge=1, le=300)

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092")
    KAFKA_CONSUMER_GROUP: str = Field(default="agent-workers")
    KAFKA_PARTITION_COUNT: int = Field(default=12, ge=1)
    KAFKA_SECURITY_PROTOCOL: str = Field(default="PLAINTEXT")
    KAFKA_SASL_MECHANISM: str = Field(default="PLAIN")
    KAFKA_SASL_USERNAME: Optional[str] = Field(default=None)
    KAFKA_SASL_PASSWORD: Optional[str] = Field(default=None)

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for agent")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")

    # Twilio WhatsApp Configuration
    TWILIO_ACCOUNT_SID: str = Field(default="")
    TWILIO_AUTH_TOKEN: str = Field(default="")
    TWILIO_WHATSAPP_NUMBER: str = Field(default="whatsapp:+14155238886")

    # Gmail API Configuration
    GMAIL_SERVICE_ACCOUNT_PATH: str = Field(default="./credentials/gmail-service-account.json")
    GMAIL_SUPPORT_EMAIL: str = Field(default="support@company.com")

    # Application Configuration
    LOG_LEVEL: str = Field(default="INFO")
    AGENT_RESPONSE_TIMEOUT: int = Field(default=180, ge=1)
    CORRELATION_ID_HEADER: str = Field(default="X-Correlation-ID")

    # Performance Configuration
    MAX_CONCURRENT_CONVERSATIONS: int = Field(default=1000, ge=1)
    KNOWLEDGE_BASE_SIMILARITY_THRESHOLD: float = Field(default=0.6, ge=0.0, le=1.0)
    MESSAGE_RETRY_MAX_ATTEMPTS: int = Field(default=5, ge=1, le=10)
    MESSAGE_RETRY_BACKOFF_FACTOR: int = Field(default=2, ge=1)

    # Security Configuration
    WEBHOOK_SECRET_KEY: str = Field(default="your-webhook-secret-key")
    JWT_ALGORITHM: str = Field(default="HS256")

    @field_validator("DB_POOL_MIN_SIZE", "DB_POOL_MAX_SIZE")
    @classmethod
    def validate_pool_sizes(cls, v: int, info) -> int:
        """Ensure pool sizes are valid."""
        if v < 1:
            raise ValueError("Pool size must be at least 1")
        return v

    @field_validator("KAFKA_BOOTSTRAP_SERVERS")
    @classmethod
    def validate_kafka_servers(cls, v: str) -> str:
        """Validate Kafka bootstrap servers format."""
        if not v or not ":" in v:
            raise ValueError("KAFKA_BOOTSTRAP_SERVERS must be in format host:port")
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure singleton pattern and avoid re-reading env vars.
    """
    return Settings()


# Convenience instance for imports
settings = get_settings()
