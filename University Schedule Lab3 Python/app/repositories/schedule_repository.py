from psycopg import AsyncConnection
from typing import List
import logging
from ..models.lab3_models import Schedule


class ScheduleRepository:
    """Репозиторий для работы с расписанием в PostgreSQL"""
    
    def __init__(self, conn: AsyncConnection):
        self.conn = conn
        self._log = logging.getLogger(__name__)
    
    async def _detect_schema(self) -> str:
        """Определить схему таблицы (PascalCase или snake_case)"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'Schedules' AND column_name = 'Id'
            """)
            result = await cursor.fetchone()
            return "pascal" if result else "snake"
    
    async def get_by_lecture_and_group(
        self, 
        lecture_ids: List[int], 
        group_id: int
    ) -> List[Schedule]:
        """Получить расписание по ID лекций и группы"""
        if not lecture_ids:
            return []
        
        schema = await self._detect_schema()
        self._log.debug("schedule schema=%s lecture_ids=%d group_id=%s", schema, len(lecture_ids), group_id)
        
        if schema == "pascal":
            query = """
                SELECT "Id", "LectureId", "GroupId", "StartTime", "EndTime"
                FROM "Schedules"
                WHERE "LectureId" = ANY(%s) AND "GroupId" = %s
            """
        else:
            query = """
                SELECT id, lecture_id, group_id, start_time, end_time
                FROM schedules
                WHERE lecture_id = ANY(%s) AND group_id = %s
            """
        
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (lecture_ids, group_id))
            rows = await cursor.fetchall()
            
            schedules = []
            for row in rows:
                schedules.append(Schedule(
                    Id=row[0],
                    LectureId=row[1],
                    GroupId=row[2],
                    start_time=row[3],
                    end_time=row[4]
                ))
            
            return schedules
