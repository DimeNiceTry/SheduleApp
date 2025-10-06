from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения Lab2"""
    postgres_dsn: str = Field(..., description="PostgreSQL connection string")
    neo4j_uri: str = Field(..., description="Neo4j bolt URI")
    neo4j_user: str = Field(..., description="Neo4j username")
    neo4j_password: str = Field(..., description="Neo4j password")

    model_config = SettingsConfigDict(env_prefix="LAB2_", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
