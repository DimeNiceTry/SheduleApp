from typing import Optional, List
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from neo4j import AsyncDriver

from app.models.lab2_models import Lecture, GroupStudentCountDto


class LectureRepository:
    """Репозиторий для работы с лекциями (PostgreSQL + Neo4j)"""
    
    def __init__(self, pg_pool: ConnectionPool, neo4j_driver: AsyncDriver) -> None:
        self._pg_pool = pg_pool
        self._neo4j = neo4j_driver
        self._table_name: Optional[str] = None
        self._columns: Optional[dict[str, str]] = None
    
    def _ensure_schema(self) -> None:
        """Определяет схему таблицы Lectures (PascalCase или snake_case)"""
        if self._table_name is not None:
            return
        
        with self._pg_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'Lectures'
                    )
                """)
                exists_pascal = cur.fetchone()[0]
        
        if exists_pascal:
            self._table_name = '"Lectures"'
            self._columns = {
                "id": '"Id"',
                "name": '"Name"',
                "requirements": '"Requirements"',
                "year": '"Year"',
                "course_id": '"CourseId"',
            }
        else:
            self._table_name = 'lectures'
            self._columns = {
                "id": 'id',
                "name": 'name',
                "requirements": 'requirements',
                "year": 'year',
                "course_id": 'course_id',
            }
    
    def get_lectures_by_course_id(self, course_id: int, year: int) -> List[Lecture]:
        """
        Получает все лекции для курса в заданном году из PostgreSQL
        
        :param course_id: ID курса
        :param year: Год
        :return: Список лекций
        """
        self._ensure_schema()
        assert self._table_name is not None and self._columns is not None
        
        query = f"""
            SELECT 
                {self._columns['id']} AS "Id",
                {self._columns['name']} AS "Name",
                {self._columns['requirements']} AS "Requirements",
                {self._columns['year']} AS "Year",
                {self._columns['course_id']} AS "CourseId"
            FROM {self._table_name}
            WHERE {self._columns['course_id']} = %s 
              AND {self._columns['year']} = %s
        """
        
        with self._pg_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, (course_id, year))
                rows = cur.fetchall()
                return [Lecture(**row) for row in rows]
    
    async def get_groups_with_student_count_for_lecture(
        self, lecture_id: int
    ) -> List[GroupStudentCountDto]:
        """
        Получает список групп и количество студентов для лекции из Neo4j
        
        :param lecture_id: ID лекции
        :return: Список GroupStudentCountDto
        """
        cypher_query = """
            MATCH (l:Lecture {id: $LectureId})
            MATCH (g:Group)-[:HAS_LECTURE]->(l)
            WITH g
            OPTIONAL MATCH (s:Student)-[:BELONGS_TO]->(g)
            RETURN g.id AS GroupId, count(s) AS StudentCount
            ORDER BY GroupId
        """
        
        results: List[GroupStudentCountDto] = []
        
        async with self._neo4j.session(database="neo4j") as session:
            try:
                cursor = await session.run(cypher_query, {"LectureId": lecture_id})
                records = await cursor.values()
                
                for record in records:
                    if record and len(record) >= 2:
                        group_id = int(record[0]) if record[0] is not None else 0
                        student_count = int(record[1]) if record[1] is not None else 0
                        results.append(
                            GroupStudentCountDto(
                                group_id=group_id, 
                                student_count=student_count
                            )
                        )
            except Exception as e:
                print(f"Error getting groups from Neo4j for lecture {lecture_id}: {e}")
        
        return results
