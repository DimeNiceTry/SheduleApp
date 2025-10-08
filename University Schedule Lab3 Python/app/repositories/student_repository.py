from redis.asyncio import Redis
from typing import List
from ..models.lab3_models import Student
import json


class StudentRepository:
    """Репозиторий для работы со студентами в Redis"""
    
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get_by_ids(self, student_ids: List[int]) -> List[Student]:
        """Получить студентов по списку ID"""
        students = []
        
        for student_id in student_ids:
            try:
                # Пытаемся получить из Redis
                data = await self.redis.get(f"student:{student_id}")
                if data:
                    student_dict = json.loads(data)
                    students.append(Student(**student_dict))
            except Exception as e:
                print(f"Error getting student {student_id}: {e}")
        
        return students
from redis.asyncio import Redis
from typing import List
from ..models.lab3_models import Student
import json
import logging


class StudentRepository:
    """Работа со студентами в Redis."""

    def __init__(self, redis: Redis):
        self.redis = redis
        self._log = logging.getLogger(__name__)

    async def get_by_ids(self, student_ids: List[int]) -> List[Student]:
        """Получить студентов по списку ID. Поддерживает hash и JSON хранение."""
        self._log.debug("redis get_by_ids: n=%d", len(student_ids))
        students: List[Student] = []
        for student_id in student_ids:
            key = f"student:{student_id}"
            try:
                # 1) Основной путь: Hash (как пишет генератор на C#)
                h = await self.redis.hgetall(key)
                if h:
                    mapped = {
                        "Id": student_id,
                        "FullName": h.get("fio") or h.get("full_name") or "",
                        "GroupId": int(h.get("id_group")) if h.get("id_group") else 0,
                        "DateOfRecipient": h.get("date_of_recipient") or h.get("date_of_recipient"),
                    }
                    students.append(Student(**mapped))
                    continue

                # 2) Fallback: JSON-строка по ключу
                raw = await self.redis.get(key)
                if raw:
                    student_dict = json.loads(raw)
                    students.append(Student(**student_dict))
            except Exception as e:
                self._log.error("redis get student %s error: %s", student_id, e)
        return students
