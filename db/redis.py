from redis.asyncio import Redis
import json


class RedisHandler:
    def __init__(self, host="redis", port=6379):
        # создаём экземпляр Redis-клиента
        self.redis = Redis(host=host, port=port, decode_responses=True)

    async def save_student(self, key, student):
        """Создание/обновление студента по ключу (зачетная книжка) используя HMSET согласно схеме"""
        # Используем HMSET структуру согласно redis.sql схеме
        student_data = {
            "fio": student.get("fio", student.get("name", "")),
            "id_group": str(student.get("id_group", student.get("group_id", 1))),
            "date_of_recipient": student.get("date_of_recipient", "2022-09-01")
        }
        
        # Redis не поддерживает HMSET напрямую в aioredis, используем hset
        await self.redis.hset(key, mapping=student_data)

    async def get_student(self, key):
        """Чтение данных студента по ключу (HGETALL согласно схеме)"""
        val = await self.redis.hgetall(key)
        return val if val else None

    async def get_all_students(self):
        """Получение всех студентов"""
        keys = await self.redis.keys("student:*")  # Ключи согласно схеме student:1
        students = []
        for key in keys:
            student = await self.get_student(key)
            if student:
                student["key"] = key  # Добавляем ключ для идентификации
                students.append(student)
        return students

    async def update_student(self, key, updated_data):
        """Обновление данных студента (используя HSET для отдельных полей)"""
        exists = await self.redis.exists(key)
        if exists:
            # Обновляем только измененные поля
            await self.redis.hset(key, mapping=updated_data)
            return True
        return False

    async def create_initial_student(self):
        """Создание начального студента согласно схеме redis.sql"""
        student_key = "student:1"
        student_data = {
            "fio": "Сухов Антон Алексеевич",
            "id_group": "1",
            "date_of_recipient": "2022-09-01"
        }
        await self.redis.hset(student_key, mapping=student_data)
        return student_key

    async def delete_student(self, key):
        """Удаление студента по ключу"""
        result = await self.redis.delete(key)
        return result > 0

    async def delete_all_students(self):
        """Удаление всех студентов"""
        keys = await self.redis.keys("student:*")
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def check_connection(self):
        """Проверка доступности Redis"""
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False
