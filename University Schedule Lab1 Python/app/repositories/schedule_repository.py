from datetime import datetime
from typing import List, Sequence

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class ScheduleRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool
        self._table_name: str | None = None
        self._columns: dict[str, str] | None = None

    def _ensure_schema(self) -> None:
        if self._table_name is not None:
            return
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'Schedules')")
                exists_pascal = cur.fetchone()[0]
        if exists_pascal:
            self._table_name = '"Schedules"'
            self._columns = {
                "id": '"Id"',
                "lecture": '"LectureId"',
                "group": '"GroupId"',
                "start": '"StartTime"',
                "end": '"EndTime"',
            }
        else:
            self._table_name = 'schedule'
            self._columns = {
                "id": 'id',
                "lecture": 'id_lect',
                "group": 'id_group',
                "start": '"startTime"',
                "end": '"endTime"',
            }

    def fetch(self, lecture_ids: Sequence[int], group_ids: Sequence[int], start: datetime, end: datetime) -> List[dict]:
        if not lecture_ids or not group_ids:
            return []
        self._ensure_schema()
        assert self._columns is not None and self._table_name is not None
        query = (
            f"SELECT {self._columns['id']} AS id, {self._columns['lecture']} AS lecture_id, "
            f"{self._columns['group']} AS group_id, {self._columns['start']} AS start_time, "
            f"{self._columns['end']} AS end_time "
            f"FROM {self._table_name} "
            "WHERE "
            f"{self._columns['lecture']} = ANY(%s) "
            "AND "
            f"{self._columns['group']} = ANY(%s) "
            "AND "
            f"{self._columns['start']} BETWEEN %s AND %s"
        )
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, (list(lecture_ids), list(group_ids), start, end))
                rows = cur.fetchall()
        return rows
