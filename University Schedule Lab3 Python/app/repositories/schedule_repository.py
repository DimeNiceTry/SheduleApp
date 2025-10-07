from psycopg import AsyncConnection
from typing import List
from ..models.lab3_models import Schedule


class ScheduleRepository:
    """Репозиторий для работы с расписанием в PostgreSQL"""
    
    def __init__(self, conn: AsyncConnection):
        self.conn = conn
    
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
        
        if schema == "pascal":
            query = """
                SELECT "Id", "LectureId", "GroupId", "Date"
                FROM "Schedules"
                WHERE "LectureId" = ANY($1) AND "GroupId" = $2
            """
        else:
            query = """
                SELECT id, lecture_id, group_id, date
                FROM schedules
                WHERE lecture_id = ANY($1) AND group_id = $2
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
                    Date=row[3]
                ))
            
            return schedules
