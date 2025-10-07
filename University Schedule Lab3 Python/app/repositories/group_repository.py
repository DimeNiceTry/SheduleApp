from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from ..models.lab3_models import Group


class GroupRepository:
    """Репозиторий для работы с группами в MongoDB"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.groups
    
    async def get_by_name(self, name: str) -> Optional[Group]:
        """Получить группу по имени"""
        try:
            # Пытаемся найти с PascalCase полями
            doc = await self.collection.find_one({"Name": name})
            if doc:
                return Group(**doc)
            
            # Если не нашли, пробуем snake_case
            doc = await self.collection.find_one({"name": name})
            if doc:
                # Преобразуем snake_case в PascalCase для модели
                return Group(
                    Id=doc.get("id"),
                    Name=doc.get("name"),
                    DepartmentId=doc.get("department_id"),
                    Year=doc.get("year")
                )
            
            return None
        except Exception as e:
            print(f"Error in get_by_name: {e}")
            return None
