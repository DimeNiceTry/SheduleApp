from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_dsn: str = Field(..., description="PostgreSQL connection string for auth storage")
    jwt_secret: str = Field(..., description="JWT signing secret")
    jwt_expire_hours: int = Field(12, description="Token lifetime in hours")
    lab1_service_url: str = Field(..., description="Base URL of the Lab1 service")
    lab2_service_url: str = Field(..., description="Base URL of the Lab2 service")
    lab3_service_url: str = Field(..., description="Base URL of the Lab3 service")
    generator_service_url: str = Field(..., description="Base URL of the Generator service")
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost", "http://localhost:8000", "https://localhost:7249"], description="Allowed CORS origins")

    model_config = SettingsConfigDict(env_prefix="GATEWAY_", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
