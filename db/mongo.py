from motor.motor_asyncio import AsyncIOMotorClient

class MongoHandler:
    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://mongo:27017")
        self.db = self.client["university"]

    async def create_university_structure(self):
        """Создание структуры университета согласно схеме mongo.js"""
        document = {
            "_id": 1,
            "name": "РТУ МИРЭА",
            "institutes": [
                {
                    "_id": 1,
                    "name": "Институт ИКБ",
                    "departments": [
                        {
                            "_id": 1,
                            "name": "Факультет разработки ПО"
                        }
                    ]
                }
            ]
        }
        
        # Используем upsert для избежания дублирования
        await self.db.universities.replace_one(
            {"_id": 1}, 
            document, 
            upsert=True
        )
        return document

    async def save_group_with_students(self, group, students):
        """Создание документа группы с составом студентов (дополнительно к universities)"""
        document = {
            "group": group,
            "students": students,
            "created_at": None,
            "updated_at": None
        }
        result = await self.db.groups.insert_one(document)
        return str(result.inserted_id)

    async def get_group(self, group_id):
        """Чтение документа группы по ID"""
        group = await self.db.groups.find_one({"group.id": group_id})
        if group:
            group["_id"] = str(group["_id"])
        return group

    async def get_university_by_department(self, department_name="Факультет разработки ПО"):
        """Получение университета по названию кафедры согласно схеме mongo.js"""
        query = {"institutes.departments.name": department_name}
        result = await self.db.universities.find_one(query)
        if result:
            result["_id"] = str(result["_id"]) if "_id" in result else None
        return result

    async def get_all_universities(self):
        """Получение всех университетов"""
        cursor = self.db.universities.find()
        universities = []
        async for university in cursor:
            if "_id" in university:
                university["_id"] = str(university["_id"])
            universities.append(university)
        return universities

    async def get_all_groups(self):
        """Получение всех групп"""
        cursor = self.db.groups.find()
        groups = []
        async for group in cursor:
            group["_id"] = str(group["_id"])
            groups.append(group)
        return groups

    async def update_group(self, group_id, updated_data):
        """Обновление данных группы"""
        result = await self.db.groups.update_one(
            {"group.id": group_id},
            {"$set": updated_data}
        )
        return result.modified_count > 0

    async def add_student_to_group(self, group_id, student):
        """Добавление студента в группу"""
        result = await self.db.groups.update_one(
            {"group.id": group_id},
            {"$push": {"students": student}}
        )
        return result.modified_count > 0

    async def remove_student_from_group(self, group_id, student_id):
        """Удаление студента из группы"""
        result = await self.db.groups.update_one(
            {"group.id": group_id},
            {"$pull": {"students": {"id": student_id}}}
        )
        return result.modified_count > 0

    async def delete_group(self, group_id):
        """Удаление группы"""
        result = await self.db.groups.delete_one({"group.id": group_id})
        return result.deleted_count > 0

    async def delete_all_groups(self):
        """Удаление всех групп"""
        result = await self.db.groups.delete_many({})
        return result.deleted_count

    async def delete_all_universities(self):
        """Удаление всех университетов"""
        result = await self.db.universities.delete_many({})
        return result.deleted_count

    async def delete_all_data(self):
        """Удаление всех данных из MongoDB"""
        groups_deleted = await self.delete_all_groups()
        universities_deleted = await self.delete_all_universities()
        return {
            "groups_deleted": groups_deleted,
            "universities_deleted": universities_deleted
        }

    async def check_connection(self):
        """Проверка доступности MongoDB"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False
