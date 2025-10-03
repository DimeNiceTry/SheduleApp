from fastapi import FastAPI, HTTPException
from services.generator import DataGenerator

app = FastAPI(
    title="ScheduleApp - Database Management System",
    description="Система для работы с различными типами баз данных: PostgreSQL, Redis, MongoDB, Neo4j, Elasticsearch",
    version="1.0.0"
)

generator = DataGenerator()

@app.get("/")
async def root():
    return {
        "message": "ScheduleApp Database Management System",
        "services": ["PostgreSQL", "Redis", "MongoDB", "Neo4j", "Elasticsearch"],
        "available_endpoints": [
            "/health - Проверка доступности служб",
            "/generate - Генерация тестовых данных",
            "/demo-crud - Демонстрация CRUD операций", 
            "/cleanup - Удаление всех данных"
        ]
    }

@app.get("/health")
async def health_check():
    """Проверка доступности всех служб"""
    services_status = await generator.check_services()
    
    all_available = all(services_status.values())
    
    return {
        "status": "healthy" if all_available else "degraded",
        "services": services_status,
        "timestamp": "2025-09-07"
    }

@app.post("/generate")
async def generate_data():
    """Генерация тестовых данных для всех служб"""
    try:
        result = await generator.generate_all()
        return {
            "status": "success",
            "message": "Данные успешно сгенерированы",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/demo-crud")
async def demo_crud():
    """Демонстрация CRUD операций для всех служб"""
    try:
        result = await generator.demo_crud_operations()
        return {
            "status": "success",
            "message": "CRUD операции выполнены",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cleanup")
async def cleanup_data():
    """Удаление всех данных из всех служб"""
    try:
        result = await generator.cleanup_all()
        return {
            "status": "success", 
            "message": "Все данные удалены",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Специфические эндпоинты для каждой службы

@app.get("/redis/students")
async def get_all_redis_students():
    """Получение всех студентов из Redis"""
    students = await generator.redis.get_all_students()
    return {"students": students, "count": len(students)}

@app.get("/redis/student/{record_book}")
async def get_redis_student(record_book: str):
    """Получение студента из Redis по номеру зачетной книжки"""
    student = await generator.redis.get_student(record_book)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student

@app.get("/mongodb/groups")
async def get_mongo_groups():
    """Получение всех групп из MongoDB"""
    groups = await generator.mongo.get_all_groups()
    return {"groups": groups, "count": len(groups)}

@app.get("/elasticsearch/search")
async def search_courses(q: str):
    """Полнотекстовый поиск курсов в Elasticsearch"""
    if not q:
        raise HTTPException(status_code=400, detail="Параметр поиска 'q' обязателен")
    
    results = await generator.elastic.search_courses(q)
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }

@app.get("/neo4j/student/{student_id}/courses")
async def get_student_courses(student_id: int):
    """Получение курсов студента из Neo4j"""
    courses = await generator.neo4j.get_student_courses(student_id)
    return {
        "student_id": student_id,
        "courses": courses,
        "count": len(courses)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
