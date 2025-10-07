from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from .database import DatabaseConnections
from .repositories.group_repository import GroupRepository
from .repositories.student_repository import StudentRepository
from .repositories.course_repository import CourseRepository
from .repositories.lecture_repository import LectureRepository
from .repositories.schedule_repository import ScheduleRepository
from .repositories.visits_repository import VisitsRepository
from .services.group_report_service import GroupReportService
from .models.lab3_models import GroupReportResponse


# Глобальное подключение к БД
db_connections = DatabaseConnections()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Подключение к БД при старте
    await db_connections.connect()
    yield
    # Отключение от БД при завершении
    await db_connections.close()


app = FastAPI(
    title="University Schedule Lab3 API",
    description="API для получения отчета по группе с информацией о специальных курсах и посещаемости",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Health"])
async def root():
    """Проверка доступности сервиса"""
    return {
        "service": "University Schedule Lab3",
        "status": "running",
        "endpoints": ["/lab3"]
    }


@app.get("/lab3", response_model=GroupReportResponse, tags=["Lab3"])
async def get_group_report(
    groupName: str = Query("ДЕФ-02-24", description="Название группы")
) -> GroupReportResponse:
    """
    Получить отчет по группе:
    - Информация о специальных курсах и лекциях департамента
    - Список студентов с общими и посещенными часами
    
    Пример: /lab3?groupName=ДЕФ-02-24
    """
    # Инициализация репозиториев
    mongo_db = db_connections.get_mongo_db()
    
    group_repo = GroupRepository(mongo_db)
    student_repo = StudentRepository(db_connections.redis_client)
    course_repo = CourseRepository(db_connections.postgres_conn)
    lecture_repo = LectureRepository(
        db_connections.postgres_conn,
        db_connections.neo4j_driver
    )
    schedule_repo = ScheduleRepository(db_connections.postgres_conn)
    visits_repo = VisitsRepository(db_connections.postgres_conn)
    
    # Инициализация сервиса
    service = GroupReportService(
        group_repo=group_repo,
        student_repo=student_repo,
        course_repo=course_repo,
        lecture_repo=lecture_repo,
        schedule_repo=schedule_repo,
        visits_repo=visits_repo
    )
    
    # Получение отчета
    return await service.get_group_report(groupName)
