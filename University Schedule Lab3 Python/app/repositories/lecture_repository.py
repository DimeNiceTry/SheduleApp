from psycopg import AsyncConnection
from neo4j import AsyncDriver
from typing import List, Tuple
from ..models.lab3_models import Lecture


class LectureRepository:
    """Репозиторий для работы с лекциями в PostgreSQL и Neo4j"""
    
    def __init__(self, pg_conn: AsyncConnection, neo4j_driver: AsyncDriver):
        self.pg_conn = pg_conn
        self.neo4j_driver = neo4j_driver
    
    async def _detect_schema(self) -> str:
        """Определить схему таблицы (PascalCase или snake_case)"""
        async with self.pg_conn.cursor() as cursor:
            await cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'Lectures' AND column_name = 'Id'
            """)
            result = await cursor.fetchone()
            return "pascal" if result else "snake"
    
    async def get_by_course_ids(self, course_ids: List[int]) -> List[Lecture]:
        """Получить лекции по ID курсов"""
        if not course_ids:
            return []
        
        schema = await self._detect_schema()
        
        if schema == "pascal":
            query = """
                SELECT "Id", "Name", "Requirements", "Year", "CourseId"
                FROM "Lectures"
                WHERE "CourseId" = ANY($1)
            """
        else:
            query = """
                SELECT id, name, requirements, year, course_id
                FROM lectures
                WHERE course_id = ANY($1)
            """
        
        async with self.pg_conn.cursor() as cursor:
            await cursor.execute(query, (course_ids,))
            rows = await cursor.fetchall()
            
            lectures = []
            for row in rows:
                lectures.append(Lecture(
                    Id=row[0],
                    Name=row[1],
                    Requirements=row[2],
                    Year=row[3],
                    CourseId=row[4]
                ))
            
            return lectures
    
    async def get_group_details(self, group_id: int) -> Tuple[List[int], List[int]]:
        """
        Получить детали группы из Neo4j: списки ID студентов и лекций
        Возвращает: (student_ids, lecture_ids)
        """
        async with self.neo4j_driver.session() as session:
            # Получаем студентов группы
            student_result = await session.run(
                """
                MATCH (g:Group {Id: $groupId})<-[:BELONGS_TO]-(s:Student)
                RETURN s.Id as studentId
                """,
                groupId=group_id
            )
            student_records = await student_result.data()
            student_ids = [record["studentId"] for record in student_records]
            
            # Получаем лекции, которые может посещать группа
            lecture_result = await session.run(
                """
                MATCH (g:Group {Id: $groupId})-[:CAN_ATTEND]->(l:Lecture)
                RETURN l.Id as lectureId
                """,
                groupId=group_id
            )
            lecture_records = await lecture_result.data()
            lecture_ids = [record["lectureId"] for record in lecture_records]
            
            return student_ids, lecture_ids
