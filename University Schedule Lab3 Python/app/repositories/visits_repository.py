from psycopg import AsyncConnection
from typing import List
import logging
from ..models.lab3_models import Visit


class VisitsRepository:
    """Репозиторий для работы с посещениями в PostgreSQL"""
    
    def __init__(self, conn: AsyncConnection):
        self.conn = conn
        self._log = logging.getLogger(__name__)
    
    async def _detect_schema(self) -> str:
        """Определить схему таблицы (PascalCase или snake_case)"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'Visits' AND column_name = 'Id'
            """)
            result = await cursor.fetchone()
            return "pascal" if result else "snake"
    
    async def get_by_schedule_and_students(
        self, 
        schedule_ids: List[int], 
        student_ids: List[int]
    ) -> List[Visit]:
        """Получить посещения по ID расписаний и студентов"""
        if not schedule_ids or not student_ids:
            return []
        
        schema = await self._detect_schema()
        self._log.debug("visits schema=%s schedule_ids=%d student_ids=%d", schema, len(schedule_ids), len(student_ids))
        
        if schema == "pascal":
            query = """
                SELECT "Id", "StudentId", "ScheduleId"
                FROM "Visits"
                WHERE "ScheduleId" = ANY(%s) AND "StudentId" = ANY(%s)
            """
        else:
            query = """
                SELECT id, student_id, schedule_id
                FROM visits
                WHERE schedule_id = ANY(%s) AND student_id = ANY(%s)
            """
        
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (schedule_ids, student_ids))
            rows = await cursor.fetchall()
            
            visits = []
            for row in rows:
                visits.append(Visit(
                    Id=row[0],
                    StudentId=row[1],
                    ScheduleId=row[2]
                ))
            
            return visits
