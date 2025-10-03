from neo4j import AsyncGraphDatabase
import random

class Neo4jHandler:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password"))

    async def create_initial_structure(self):
        """Создание структуры согласно схеме neo4j.sql"""
        async with self.driver.session() as session:
            # Создание лекции согласно схеме
            await session.run("""
                MERGE (l:Lecture {
                    id: 1, 
                    name: 'Введение в архитектуру ПО', 
                    requirments: true
                })
            """)

            # Создание группы согласно схеме  
            await session.run("""
                MERGE (g:Group {
                    id: 1, 
                    name: 'БСБО-01-22', 
                    startYear: '2022-09-01', 
                    endYear: '2026-06-30'
                })
            """)

            # Создание студента согласно схеме
            await session.run("""
                MERGE (s:Student {
                    id: 1, 
                    fio: 'Сухов Антон Алексеевич', 
                    date_of_recipient: '2022-09-01'
                })
            """)

            # Создание связи студент-лекция (ATTENDED)
            await session.run("""
                MATCH (s:Student {id: 1}), (l:Lecture {id: 1})
                MERGE (s)-[:ATTENDED {visitTime: '2023-09-01T10:41:00'}]->(l)
            """)

            # Создание связи группа-лекция (HAS_LECTURE)
            await session.run("""
                MATCH (g:Group {id: 1}), (l:Lecture {id: 1})
                MERGE (g)-[:HAS_LECTURE {
                    startTime: '2023-02-10T10:40:00',
                    endTime: '2025-02-10T12:10:00'
                }]->(l)
            """)

    async def create_relations(self, students, courses, group):
        """Создание связей между группой, студентами и курсами (дополнительно)"""
        async with self.driver.session() as session:
            # Создание группы
            await session.run(
                "MERGE (g:Group {id:$id, name:$name})",
                id=group["id"], name=group.get("title", group.get("name", ""))
            )
            
            # Создание студентов и связи с группой
            for s in students:
                await session.run(
                    "MERGE (s:Student {id:$id, fio:$fio})",
                    id=s["id"], fio=s.get("name", s.get("fio", ""))
                )
                await session.run(
                    "MATCH (g:Group {id:$gid}), (s:Student {id:$sid}) "
                    "MERGE (g)-[:HAS_STUDENT]->(s)",
                    gid=group["id"], sid=s["id"]
                )
            
            # Создание лекций из курсов
            for c in courses:
                await session.run(
                    "MERGE (l:Lecture {id:$id, name:$name, requirments:$req})",
                    id=c["id"], name=c.get("title", c.get("name", "")), req=True
                )
                
                # Случайные посещения лекций студентами
                for s in students:
                    if random.choice([True, False]):  # 50% вероятность посещения
                        await session.run(
                            "MATCH (s:Student {id:$sid}), (l:Lecture {id:$lid}) "
                            "MERGE (s)-[:ATTENDED {visitTime: datetime()}]->(l)",
                            sid=s["id"], lid=c["id"]
                        )

    async def get_student(self, student_id):
        """Получение студента по ID"""
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (s:Student {id:$id}) RETURN s",
                id=student_id
            )
            record = await result.single()
            return dict(record["s"]) if record else None

    async def get_group_students(self, group_id):
        """Получение всех студентов группы"""
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (g:Group {id:$id})-[:HAS_STUDENT]->(s:Student) RETURN s",
                id=group_id
            )
            students = []
            async for record in result:
                students.append(dict(record["s"]))
            return students

    async def get_student_lectures(self, student_id):
        """Получение лекций, которые посещал студент (согласно схеме ATTENDED)"""
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (s:Student {id:$id})-[r:ATTENDED]->(l:Lecture) "
                "RETURN l, r.visitTime as visitTime",
                id=student_id
            )
            lectures = []
            async for record in result:
                lecture = dict(record["l"])
                lecture["visitTime"] = record["visitTime"]
                lectures.append(lecture)
            return lectures

    async def get_student_courses(self, student_id):
        """Получение курсов студента (обратная совместимость)"""
        return await self.get_student_lectures(student_id)

    async def enroll_student_in_course(self, student_id, course_id):
        """Запись студента на курс"""
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (s:Student {id:$sid}), (c:Course {id:$cid}) "
                "MERGE (s)-[:ENROLLED_IN]->(c) "
                "RETURN s, c",
                sid=student_id, cid=course_id
            )
            return await result.single() is not None

    async def unenroll_student_from_course(self, student_id, course_id):
        """Отчисление студента с курса"""
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (s:Student {id:$sid})-[r:ENROLLED_IN]->(c:Course {id:$cid}) "
                "DELETE r "
                "RETURN count(r) as deleted",
                sid=student_id, cid=course_id
            )
            record = await result.single()
            return record["deleted"] > 0

    async def update_student(self, student_id, **updates):
        """Обновление данных студента"""
        async with self.driver.session() as session:
            set_clause = ", ".join([f"s.{key} = ${key}" for key in updates.keys()])
            query = f"MATCH (s:Student {{id:$id}}) SET {set_clause} RETURN s"
            
            params = {"id": student_id, **updates}
            result = await session.run(query, params)
            return await result.single() is not None

    async def delete_student(self, student_id):
        """Удаление студента и всех его связей"""
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (s:Student {id:$id}) "
                "DETACH DELETE s "
                "RETURN count(s) as deleted",
                id=student_id
            )
            record = await result.single()
            return record["deleted"] > 0

    async def delete_all_data(self):
        """Удаление всех данных"""
        async with self.driver.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")

    async def check_connection(self):
        """Проверка доступности Neo4j"""
        try:
            async with self.driver.session() as session:
                await session.run("RETURN 1")
            return True
        except Exception:
            return False

    async def close(self):
        """Закрытие соединения"""
        await self.driver.close()
