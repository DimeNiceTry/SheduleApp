from elasticsearch import Elasticsearch
from neo4j import GraphDatabase, Driver
from psycopg_pool import ConnectionPool
import redis

from .config import get_settings


settings = get_settings()
_pg_pool = ConnectionPool(settings.postgres_dsn, min_size=1, max_size=10, kwargs={"prepare_threshold": 0})
_elastic_client = Elasticsearch(settings.elastic_url)
_neo4j_driver: Driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
    max_connection_lifetime=3600,
)
_redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get_pg_pool() -> ConnectionPool:
    return _pg_pool


def get_elastic() -> Elasticsearch:
    return _elastic_client


def get_neo4j_driver() -> Driver:
    return _neo4j_driver


def get_redis() -> redis.Redis:
    return _redis_client


async def startup() -> None:
    # Open the pool eagerly so connection issues fail fast during startup.
    _pg_pool.open()
    try:
        _elastic_client.ping()
    except Exception:
        # The application can still start; the real error will surface on first use.
        pass


async def shutdown() -> None:
    _pg_pool.close()
    _neo4j_driver.close()
    _redis_client.close()
    _elastic_client.close()
