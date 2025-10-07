from typing import Optional
from urllib.parse import urlparse

import psycopg
from psycopg import sql
from psycopg_pool import ConnectionPool

from ..config import get_settings


_settings = get_settings()
_pool: Optional[ConnectionPool] = None


def _ensure_database() -> None:
    """Ensure target database exists by connecting to admin DB and creating it if missing."""
    dsn = _settings.postgres_dsn
    u = urlparse(dsn)
    target_db = (u.path or '').lstrip('/') or 'postgres'
    admin_user = u.username or 'postgres'
    admin_pass = u.password or ''
    admin_host = u.hostname or 'postgres'
    admin_port = u.port or 5432
    admin_dsn = f"postgresql://{admin_user}:{admin_pass}@{admin_host}:{admin_port}/postgres"

    try:
        with psycopg.connect(admin_dsn) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
                exists = cur.fetchone() is not None
                if not exists:
                    cur.execute(sql.SQL("CREATE DATABASE {} ").format(sql.Identifier(target_db)))
    except Exception:
        # If creation fails (insufficient perms or race), pool will still try to connect and error clearly.
        pass


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _ensure_database()
        _pool = ConnectionPool(_settings.postgres_dsn, min_size=1, max_size=5, kwargs={"prepare_threshold": 0})
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
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)


def shutdown_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
