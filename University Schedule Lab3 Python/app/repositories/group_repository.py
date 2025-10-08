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
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from ..models.lab3_models import Group
from psycopg import AsyncConnection


class GroupRepository:
    """Доступ к данным группы: первично MongoDB (коллекция groups),
    при отсутствии документа — fallback в Postgres (таблица Groups)."""

    def __init__(self, db: AsyncIOMotorDatabase, pg_conn: Optional[AsyncConnection] = None):
        self.db = db
        self.collection = db.groups
        self.pg_conn = pg_conn

    async def get_by_name(self, name: str) -> Optional[Group]:
        """Получить группу по её названию."""
        try:
            # 1) Mongo, PascalCase
            doc = await self.collection.find_one({"Name": name})
            if doc:
                return Group(**doc)

            # 2) Mongo, snake_case (handle id/_id)
            doc = await self.collection.find_one({"name": name})
            if doc:
                gid = doc.get("id", doc.get("_id"))
                return Group(
                    Id=int(gid) if gid is not None else 0,
                    Name=doc.get("name"),
                    DepartmentId=int(doc.get("department_id")) if doc.get("department_id") is not None else 0,
                    Year=int(doc.get("year")) if doc.get("year") is not None else 0,
                )

            # 3) Fallback: Postgres
            if self.pg_conn:
                # Try PascalCase schema first
                async with self.pg_conn.cursor() as cursor:
                    try:
                        await cursor.execute(
                            'SELECT "Id", "Name", "DepartmentId", EXTRACT(YEAR FROM "StartYear")::int AS "Year" '
                            'FROM "Groups" WHERE "Name" = %s',
                            (name,)
                        )
                        row = await cursor.fetchone()
                        if row:
                            return Group(
                                Id=int(row[0]),
                                Name=row[1],
                                DepartmentId=int(row[2]),
                                Year=int(row[3])
                            )
                    except Exception:
                        pass
                    # Fallback to snake_case schema
                    try:
                        await cursor.execute(
                            'SELECT id, name, department_id, EXTRACT(YEAR FROM start_year)::int AS year '
                            'FROM groups WHERE name = %s',
                            (name,)
                        )
                        row = await cursor.fetchone()
                        if row:
                            return Group(
                                Id=int(row[0]),
                                Name=row[1],
                                DepartmentId=int(row[2]),
                                Year=int(row[3])
                            )
                    except Exception:
                        pass
            return None
        except Exception as e:
            print(f"Error in get_by_name: {e}")
            return None
