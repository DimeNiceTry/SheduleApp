from typing import Optional

from psycopg.rows import dict_row

from .session import get_pool


class UserRepository:
    def __init__(self) -> None:
        self._pool = get_pool()

    def create(self, name: str, password_hash: str) -> None:
        query = "INSERT INTO users(name, password_hash) VALUES (%s, %s)"
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, password_hash))

    def get_by_name(self, name: str) -> Optional[dict]:
        query = "SELECT id, name, password_hash FROM users WHERE name = %s"
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, (name,))
                row = cur.fetchone()
        return row
