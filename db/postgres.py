
import asyncpg
import random
from datetime import datetime, timedelta

class PostgresHandler:
    def __init__(self):
        self.dsn = "postgresql://postgres:postgres@postgres:5432/university"

    async def _get_conn(self):
        return await asyncpg.connect(self.dsn)

    async def create_tables(self):
        """Создание таблиц согласно схеме Postgres.sql"""
        conn = await self._get_conn()
        try:
            # Создание таблиц согласно схеме
            
            # Университеты
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS universities (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
            
            # Институты
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS institutes (
                    id INTEGER PRIMARY KEY,
                    id_univer INTEGER,
                    name TEXT,
                    FOREIGN KEY (id_univer) REFERENCES universities (id)
                )
            """)
            
            # Кафедры
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY,
                    id_institutes INTEGER,
                    name TEXT,
                    FOREIGN KEY (id_institutes) REFERENCES institutes (id)
                )
            """)
            
            # Группы
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY,
                    id_kafedra INTEGER,
                    name TEXT,
                    "startYear" DATE,
                    "endYear" DATE,
                    FOREIGN KEY (id_kafedra) REFERENCES departments (id)
                )
            """)
            
            # Студенты
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    id_group INTEGER,
                    fio TEXT,
                    date_of_recipient DATE,
                    FOREIGN KEY (id_group) REFERENCES groups (id)
                )
            """)
            
            # Специальности
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS specialties (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    code TEXT
                )
            """)
            
            # Курсы
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY,
                    id_kadefra INTEGER,
                    id_spec INTEGER,
                    name TEXT,
                    term TEXT,
                    FOREIGN KEY (id_kadefra) REFERENCES departments (id),
                    FOREIGN KEY (id_spec) REFERENCES specialties (id)
                )
            """)
            
            # Лекции
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS lectures (
                    id INTEGER PRIMARY KEY,
                    id_course INTEGER,
                    name TEXT,
                    requirments BOOLEAN,
                    FOREIGN KEY (id_course) REFERENCES courses (id)
                )
            """)
            
            # Материалы
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY,
                    id_lect INTEGER,
                    name TEXT,
                    FOREIGN KEY (id_lect) REFERENCES lectures (id)
                )
            """)
            
            # Расписания
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schedule (
                    id INTEGER PRIMARY KEY,
                    id_lect INTEGER,
                    id_group INTEGER,
                    "startTime" TIMESTAMPTZ,
                    "endTime" TIMESTAMPTZ,
                    FOREIGN KEY (id_lect) REFERENCES lectures (id),
                    FOREIGN KEY (id_group) REFERENCES groups (id)
                )
            """)
            
            # Посещения (партиционированная таблица по неделям)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL,
                    code_student INTEGER,
                    id_rasp INTEGER,
                    "visitTime" TIMESTAMPTZ,
                    week_number INTEGER NOT NULL,
                    PRIMARY KEY (id, week_number),
                    FOREIGN KEY (code_student) REFERENCES students (id),
                    FOREIGN KEY (id_rasp) REFERENCES schedule (id)
                ) PARTITION BY RANGE (week_number)
            """)
            
            # Создание партиций по неделям (52 недели)
            for week in range(1, 53):
                try:
                    await conn.execute(f"""
                        CREATE TABLE IF NOT EXISTS visits_week_{week} 
                        PARTITION OF visits 
                        FOR VALUES FROM ({week}) TO ({week + 1})
                    """)
                except:
                    pass  # Партиция уже существует
                    
            # Вставка начальных данных согласно схеме
            await self._insert_initial_data(conn)
                    
        finally:
            await conn.close()

    async def _insert_initial_data(self, conn):
        """Вставка начальных данных согласно схеме Postgres.sql"""
        try:
            # Добавление университета РТУ МИРЭА
            await conn.execute("""
                INSERT INTO universities (id, name) VALUES (1, 'РТУ МИРЭА')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление института ИКБ
            await conn.execute("""
                INSERT INTO institutes (id, id_univer, name) 
                VALUES (1, 1, 'Институт ИКБ')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление кафедры разработки ПО
            await conn.execute("""
                INSERT INTO departments (id, id_institutes, name) 
                VALUES (1, 1, 'Факультет разработки ПО')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление группы
            await conn.execute("""
                INSERT INTO groups (id, id_kafedra, name, "startYear", "endYear")
                VALUES (1, 1, 'БСБО-01-22', '2022-09-01', '2026-06-30')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление студента
            await conn.execute("""
                INSERT INTO students (id, id_group, fio, date_of_recipient)
                VALUES (1, 1, 'Сухов Антон Алексеевич', '2022-09-01')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление специальности
            await conn.execute("""
                INSERT INTO specialties (id, name, code)
                VALUES (1, 'Информационные системы и технологии', '09.03.02')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление курса
            await conn.execute("""
                INSERT INTO courses (id, id_kadefra, id_spec, name, term)
                VALUES (1, 1, 1, 'Проектирование архитектуры программного обеспечения', '2025-2026')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление лекции
            await conn.execute("""
                INSERT INTO lectures (id, id_course, name, requirments)
                VALUES (1, 1, 'Введение в архитектуру ПО', true)
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление материалов к лекции
            await conn.execute("""
                INSERT INTO materials (id, id_lect, name)
                VALUES (1, 1, 'Лекция 1: Основные концепции')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление расписания
            await conn.execute("""
                INSERT INTO schedule (id, id_lect, id_group, "startTime", "endTime")
                VALUES (1, 1, 1, '2023-02-10 10:40:00', '2025-02-10 12:10:00')
                ON CONFLICT (id) DO NOTHING
            """)

            # Добавление посещения
            await conn.execute("""
                INSERT INTO visits (id, code_student, id_rasp, "visitTime", week_number)
                VALUES (1, 1, 1, '2023-09-01 10:41:00', 1)
                ON CONFLICT (id, week_number) DO NOTHING
            """)
        except Exception as e:
            print(f"Ошибка вставки начальных данных: {e}")

    async def insert_students(self, students):
        conn = await self._get_conn()
        try:
            for s in students:
                await conn.execute("""
                    INSERT INTO students(id, name, record_book) 
                    VALUES($1,$2,$3) 
                    ON CONFLICT (record_book) DO NOTHING
                """, s["id"], s["name"], s["record_book"])
        finally:
            await conn.close()

    async def insert_courses(self, courses):
        conn = await self._get_conn()
        try:
            for c in courses:
                await conn.execute("""
                    INSERT INTO courses(id, title, description) 
                    VALUES($1,$2,$3) 
                    ON CONFLICT (id) DO NOTHING
                """, c["id"], c["title"], c["desc"])
        finally:
            await conn.close()

    async def insert_groups(self, groups):
        conn = await self._get_conn()
        try:
            for g in groups:
                await conn.execute("""
                    INSERT INTO groups(id, title) 
                    VALUES($1,$2) 
                    ON CONFLICT (id) DO NOTHING
                """, g["id"], g["title"])
        finally:
            await conn.close()

    async def generate_attendance_data(self, students, courses):
        """Генерация случайных данных о посещении с партиционированием по неделям"""
        conn = await self._get_conn()
        try:
            start_date = datetime(2025, 9, 1)  # Начало семестра
            
            for week in range(1, 17):  # 16 недель семестра
                for student in students:
                    for course in courses:
                        # Случайная дата в рамках недели
                        week_start = start_date + timedelta(weeks=week-1)
                        attendance_date = week_start + timedelta(days=random.randint(0, 6))
                        
                        # Случайное посещение (80% вероятность присутствия)
                        is_present = random.random() < 0.8
                        
                        await conn.execute("""
                            INSERT INTO attendance(student_id, course_id, attendance_date, week_number, is_present)
                            VALUES($1, $2, $3, $4, $5)
                        """, student["id"], course["id"], attendance_date, week, is_present)
        finally:
            await conn.close()

    # CRUD операции
    async def get_student_by_id(self, student_id):
        conn = await self._get_conn()
        try:
            result = await conn.fetchrow("SELECT * FROM students WHERE id = $1", student_id)
            return dict(result) if result else None
        finally:
            await conn.close()

    async def update_student(self, student_id, name=None, record_book=None):
        conn = await self._get_conn()
        try:
            if name:
                await conn.execute("UPDATE students SET name = $1 WHERE id = $2", name, student_id)
            if record_book:
                await conn.execute("UPDATE students SET record_book = $1 WHERE id = $2", record_book, student_id)
        finally:
            await conn.close()

    async def delete_student(self, student_id):
        conn = await self._get_conn()
        try:
            await conn.execute("DELETE FROM students WHERE id = $1", student_id)
        finally:
            await conn.close()

    async def drop_tables(self):
        """Удаление всех таблиц согласно схеме"""
        conn = await self._get_conn()
        try:
            # Удаляем в обратном порядке из-за foreign key зависимостей
            await conn.execute("DROP TABLE IF EXISTS visits CASCADE")
            await conn.execute("DROP TABLE IF EXISTS materials CASCADE")
            await conn.execute("DROP TABLE IF EXISTS schedule CASCADE")
            await conn.execute("DROP TABLE IF EXISTS lectures CASCADE")
            await conn.execute("DROP TABLE IF EXISTS courses CASCADE")
            await conn.execute("DROP TABLE IF EXISTS specialties CASCADE")
            await conn.execute("DROP TABLE IF EXISTS students CASCADE")
            await conn.execute("DROP TABLE IF EXISTS groups CASCADE")
            await conn.execute("DROP TABLE IF EXISTS departments CASCADE")
            await conn.execute("DROP TABLE IF EXISTS institutes CASCADE")
            await conn.execute("DROP TABLE IF EXISTS universities CASCADE")
        finally:
            await conn.close()

    async def check_connection(self):
        """Проверка доступности PostgreSQL"""
        try:
            conn = await self._get_conn()
            await conn.execute("SELECT 1")
            await conn.close()
            return True
        except Exception as e:
            return False
