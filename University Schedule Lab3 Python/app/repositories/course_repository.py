from psycopg import AsyncConnection
from typing import List
from ..models.lab3_models import Course


class CourseRepository:
    """Репозиторий для работы с курсами в PostgreSQL"""
    
    def __init__(self, conn: AsyncConnection):
        self.conn = conn
    
    async def _detect_schema(self) -> str:
        """Определить схему таблицы (PascalCase или snake_case)"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'Courses' AND column_name = 'Id'
            """)
            result = await cursor.fetchone()
            return "pascal" if result else "snake"
    
    async def get_by_lecture_ids_and_department(
        self, 
        lecture_ids: List[int], 
        department_id: int
    ) -> List[Course]:
        """Получить курсы по ID лекций и департаменту (специальные курсы)"""
        if not lecture_ids:
            return []
        
        schema = await self._detect_schema()
        
        if schema == "pascal":
            query = """
                SELECT "Id", "Name", "DepartmentId", "SpecialityId", "Term"
                FROM "Courses"
                WHERE "Id" IN (
                    SELECT "CourseId" FROM "Lectures" WHERE "Id" = ANY($1)
                )
                AND "DepartmentId" = $2
            """
        else:
            query = """
                SELECT id, name, department_id, speciality_id, term
                FROM courses
                WHERE id IN (
                    SELECT course_id FROM lectures WHERE id = ANY($1)
                )
                AND department_id = $2
            """
        
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (lecture_ids, department_id))
            rows = await cursor.fetchall()
            
            courses = []
            for row in rows:
                if schema == "pascal":
                    courses.append(Course(
                        Id=row[0],
                        Name=row[1],
                        DepartmentId=row[2],
                        SpecialityId=row[3],
                        Term=row[4]
                    ))
                else:
                    courses.append(Course(
                        Id=row[0],
                        Name=row[1],
                        DepartmentId=row[2],
                        SpecialityId=row[3],
                        Term=row[4]
                    ))
            
            return courses
