from psycopg_pool import ConnectionPool

from ..config import get_settings


_settings = get_settings()
_pool = ConnectionPool(_settings.postgres_dsn, min_size=1, max_size=5, kwargs={"prepare_threshold": 0})


def get_pool() -> ConnectionPool:
    return _pool


def init_schema() -> None:
    ddl = (
        "CREATE TABLE IF NOT EXISTS users ("
        "id SERIAL PRIMARY KEY,"
        "name TEXT NOT NULL UNIQUE,"
        "password_hash TEXT NOT NULL,"
        "created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
        ")"
    )
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)


def shutdown_pool() -> None:
    _pool.close()
