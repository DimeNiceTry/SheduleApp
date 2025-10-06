from typing import Iterable, List

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class VisitsRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool
        self._table_name: str | None = None
        self._columns: dict[str, str] | None = None

    def _ensure_schema(self) -> None:
        if self._table_name is not None:
            return
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'Visits'
                    )
                """)
                exists_pascal = cur.fetchone()[0]
        if exists_pascal:
            self._table_name = '"Visits"'
            self._columns = {
                "id": '"Id"',
                "student": '"StudentId"',
                "schedule": '"ScheduleId"',
            }
        else:
            self._table_name = 'visits'
            self._columns = {
                "id": 'id',
                "student": 'student_id',
                "schedule": 'schedule_id',
            }

    def fetch_by_schedule(self, schedule_ids: Iterable[int]) -> List[dict]:
        ids = [int(i) for i in schedule_ids if i is not None]
        if not ids:
            return []
        self._ensure_schema()
        assert self._table_name is not None and self._columns is not None
        placeholders = "%s"
        query = (
            f"SELECT {self._columns['id']} AS id, {self._columns['student']} AS student_id, "
            f"{self._columns['schedule']} AS schedule_id "
            f"FROM {self._table_name} "
            "WHERE "
            f"{self._columns['schedule']} = ANY(%s)"
        )
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, (ids,))
                rows = cur.fetchall()
        return rows
