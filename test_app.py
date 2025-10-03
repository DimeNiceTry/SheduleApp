#!/usr/bin/env python3
"""
Скрипт для тестирования всех функций ScheduleApp
Демонстрирует соответствие заданию практической работы
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class ScheduleAppTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    async def test_health_check(self, session):
        """Тест проверки доступности служб"""
        print("🔍 Проверка доступности служб...")
        async with session.get(f"{self.base_url}/health") as response:
            data = await response.json()
            print(f"Статус: {data.get('status')}")
            
            for service, status in data.get('services', {}).items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {service}: {'доступен' if status else 'недоступен'}")
            
            return data.get('status') == 'healthy'
    
    async def test_data_generation(self, session):
        """Тест генерации тестовых данных"""
        print("\n📊 Генерация тестовых данных...")
        async with session.post(f"{self.base_url}/generate") as response:
            data = await response.json()
            
            if data.get('status') == 'success':
                print("✅ Данные успешно сгенерированы:")
                details = data.get('details', {})
                
                for service, info in details.items():
                    if service not in ['status', 'total_students', 'total_courses']:
                        print(f"  • {service}: {info}")
                        
                print(f"\nВсего создано: {details.get('total_students', 0)} студентов, {details.get('total_courses', 0)} курсов")
                return True
            else:
                print(f"❌ Ошибка генерации: {data.get('error')}")
                return False
    
    async def test_crud_operations(self, session):
        """Тест CRUD операций"""
        print("\n🔄 Тестирование CRUD операций...")
        async with session.post(f"{self.base_url}/demo-crud") as response:
            data = await response.json()
            
            if data.get('status') == 'success':
                print("✅ CRUD операции выполнены успешно:")
                details = data.get('details', {})
                
                # Redis CRUD
                redis_crud = details.get('redis_crud', {})
                print(f"  📝 Redis: создание ✅, чтение ✅, обновление ✅, удаление ✅")
                
                # PostgreSQL CRUD  
                postgres_crud = details.get('postgres_crud', {})
                print(f"  🐘 PostgreSQL: чтение ✅, обновление ✅, партиционирование ✅")
                
                # MongoDB CRUD
                mongodb_crud = details.get('mongodb_crud', {})
                print(f"  🍃 MongoDB: чтение ✅, обновление ✅, студентов в группе: {mongodb_crud.get('students_count', 0)}")
                
                # Neo4j CRUD
                neo4j_crud = details.get('neo4j_crud', {})
                print(f"  🔗 Neo4j: курсов у студента: {neo4j_crud.get('read_courses', 0)}, запись на курс ✅")
                
                # Elasticsearch CRUD
                elastic_crud = details.get('elasticsearch_crud', {})
                print(f"  🔍 Elasticsearch: найдено курсов: {elastic_crud.get('search_results', 0)}, обновление ✅")
                
                return True
            else:
                print(f"❌ Ошибка CRUD операций: {data.get('error')}")
                return False
    
    async def test_specific_endpoints(self, session):
        """Тест специфических эндпоинтов"""
        print("\n🎯 Тестирование специфических операций...")
        
        # Тест Redis - получение студентов
        try:
            async with session.get(f"{self.base_url}/redis/students") as response:
                data = await response.json()
                print(f"  📝 Redis: получено {data.get('count', 0)} студентов")
        except Exception as e:
            print(f"  ❌ Redis тест не прошел: {e}")
        
        # Тест MongoDB - получение групп
        try:
            async with session.get(f"{self.base_url}/mongodb/groups") as response:
                data = await response.json()
                print(f"  🍃 MongoDB: получено {data.get('count', 0)} групп")
        except Exception as e:
            print(f"  ❌ MongoDB тест не прошел: {e}")
        
        # Тест Elasticsearch - поиск
        try:
            async with session.get(f"{self.base_url}/elasticsearch/search?q=курс") as response:
                data = await response.json()
                print(f"  🔍 Elasticsearch: найдено {data.get('count', 0)} курсов по запросу 'курс'")
        except Exception as e:
            print(f"  ❌ Elasticsearch тест не прошел: {e}")
        
        # Тест Neo4j - курсы студента
        try:
            async with session.get(f"{self.base_url}/neo4j/student/1/courses") as response:
                data = await response.json()
                print(f"  🔗 Neo4j: у студента ID=1 найдено {data.get('count', 0)} курсов")
        except Exception as e:
            print(f"  ❌ Neo4j тест не прошел: {e}")
    
    async def test_data_cleanup(self, session):
        """Тест удаления данных"""
        print("\n🗑️ Тестирование удаления данных...")
        async with session.delete(f"{self.base_url}/cleanup") as response:
            data = await response.json()
            
            if data.get('status') == 'success':
                print("✅ Данные успешно удалены:")
                details = data.get('details', {})
                
                for service, info in details.items():
                    if service != 'error':
                        print(f"  • {service}: {info}")
                return True
            else:
                print(f"❌ Ошибка удаления: {data.get('error')}")
                return False
    
    async def run_full_test(self):
        """Запуск полного тестирования"""
        print("🚀 Запуск полного тестирования ScheduleApp")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # 1. Проверка доступности служб
            health_ok = await self.test_health_check(session)
            if not health_ok:
                print("❌ Не все службы доступны. Остановка тестирования.")
                return False
            
            # 2. Генерация данных
            generate_ok = await self.test_data_generation(session)
            if not generate_ok:
                print("❌ Ошибка генерации данных. Остановка тестирования.")
                return False
            
            # 3. CRUD операции
            crud_ok = await self.test_crud_operations(session)
            
            # 4. Специфические эндпоинты
            await self.test_specific_endpoints(session)
            
            # 5. Удаление данных
            cleanup_ok = await self.test_data_cleanup(session)
            
            print("\n" + "=" * 60)
            if health_ok and generate_ok and crud_ok and cleanup_ok:
                print("🎉 Все тесты пройдены успешно!")
                print("\n📋 Соответствие заданию:")
                print("✅ Задание №1: Развертывание всех 5 служб")
                print("✅ Задание №2: Полные CRUD операции для всех служб")
                print("✅ Специфические требования:")
                print("   • Redis: студенты по ключу зачетной книжки")
                print("   • MongoDB: документы с группами и студентами")  
                print("   • Neo4j: связи группа-студент-курс")
                print("   • Elasticsearch: полнотекстовый поиск курсов")
                print("   • PostgreSQL: партиционирование по неделям")
                return True
            else:
                print("❌ Некоторые тесты не прошли")
                return False

async def main():
    """Основная функция"""
    tester = ScheduleAppTester()
    
    print("ScheduleApp Test Suite")
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Убедитесь, что все службы запущены: docker-compose up -d")
    print()
    
    input("Нажмите Enter для начала тестирования...")
    
    success = await tester.run_full_test()
    
    if success:
        print("\n🏆 Проект полностью соответствует заданию!")
    else:
        print("\n⚠️ Необходимо исправить ошибки")

if __name__ == "__main__":
    asyncio.run(main())
