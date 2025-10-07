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
