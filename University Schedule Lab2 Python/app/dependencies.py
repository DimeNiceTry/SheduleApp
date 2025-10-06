from neo4j import GraphDatabase, AsyncGraphDatabase, AsyncDriver
from psycopg_pool import ConnectionPool

from .config import get_settings


settings = get_settings()

# Инициализация пула подключений PostgreSQL
_pg_pool = ConnectionPool(
    settings.postgres_dsn, 
    min_size=1, 
    max_size=10, 
    kwargs={"prepare_threshold": 0}
)

# Инициализация асинхронного драйвера Neo4j
_neo4j_driver: AsyncDriver = AsyncGraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
    max_connection_lifetime=3600,
)


def get_pg_pool() -> ConnectionPool:
    """Получить пул подключений PostgreSQL"""
    return _pg_pool


def get_neo4j_driver() -> AsyncDriver:
    """Получить драйвер Neo4j"""
    return _neo4j_driver


async def startup() -> None:
    """Инициализация при запуске приложения"""
    _pg_pool.open()


async def shutdown() -> None:
    """Очистка ресурсов при остановке приложения"""
    _pg_pool.close()
    await _neo4j_driver.close()
