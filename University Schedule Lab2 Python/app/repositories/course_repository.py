from typing import Optional
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.models.lab2_models import Course


class CourseRepository:
    """Репозиторий для работы с курсами в PostgreSQL"""
    
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool
        self._table_name: Optional[str] = None
        self._columns: Optional[dict[str, str]] = None
    
    def _ensure_schema(self) -> None:
        """Определяет схему таблицы (PascalCase или snake_case)"""
        if self._table_name is not None:
            return
        
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                # Проверяем существование таблицы Courses (PascalCase)
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'Courses'
                    )
                """)
                exists_pascal = cur.fetchone()[0]
        
        if exists_pascal:
            self._table_name = '"Courses"'
            self._columns = {
                "id": '"Id"',
                "name": '"Name"',
                "department_id": '"DepartmentId"',
                "speciality_id": '"SpecialityId"',
                "term": '"Term"',
            }
        else:
            self._table_name = 'courses'
            self._columns = {
                "id": 'id',
                "name": 'name',
                "department_id": 'department_id',
                "speciality_id": 'speciality_id',
                "term": 'term',
            }
    
    def get_course_by_name(self, course_name: str) -> Optional[Course]:
        """
        Получает курс по имени с использованием ILIKE для нечеткого поиска
        
        :param course_name: Имя курса для поиска
        :return: Курс или None, если не найден
        """
        if not course_name:
            return None
        
        self._ensure_schema()
        assert self._table_name is not None and self._columns is not None
        
        query = f"""
            SELECT 
                {self._columns['id']} AS "Id",
                {self._columns['name']} AS "Name",
                {self._columns['department_id']} AS "DepartmentId",
                {self._columns['speciality_id']} AS "SpecialityId",
                {self._columns['term']} AS "Term"
            FROM {self._table_name}
            WHERE {self._columns['name']} ILIKE %s
            LIMIT 1
        """
        
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, (course_name,))
                row = cur.fetchone()
                
                if row:
                    return Course(**row)
                return None
