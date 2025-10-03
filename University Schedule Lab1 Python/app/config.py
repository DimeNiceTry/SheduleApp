from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_dsn: str = Field(..., description="PostgreSQL connection string")
    redis_url: str = Field(..., description="Redis connection URL")
    elastic_url: str = Field(..., description="Elasticsearch endpoint URL")
    elastic_index: str = Field("materials", description="Default Elasticsearch index")
    neo4j_uri: str = Field(..., description="Neo4j bolt URI")
    neo4j_user: str = Field(..., description="Neo4j username")
    neo4j_password: str = Field(..., description="Neo4j password")
    report_limit: int = Field(10, description="Maximum number of students in report")
    elastic_search_limit: int = Field(3000, description="Maximum documents to fetch from Elasticsearch")

    model_config = SettingsConfigDict(env_prefix="LAB1_", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
