from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

from app import dependencies
from app.repositories.course_repository import CourseRepository
from app.repositories.lecture_repository import LectureRepository
from app.services.report_service import ReportService
from app.models.lab2_models import CourseReportResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    await dependencies.startup()
    yield
    await dependencies.shutdown()


app = FastAPI(
    title="University Schedule Lab2 API",
    description="API для получения отчетов по курсам и лекциям",
    version="1.0.0",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_report_service() -> ReportService:
    """Dependency для получения сервиса отчетов"""
    pg_pool = dependencies.get_pg_pool()
    neo4j_driver = dependencies.get_neo4j_driver()
    
    course_repo = CourseRepository(pg_pool)
    lecture_repo = LectureRepository(pg_pool, neo4j_driver)
    
    return ReportService(course_repo, lecture_repo)


@app.get(
    "/lab2",
    response_model=CourseReportResponse,
    summary="Получить отчет по курсу",
    description=(
        "Возвращает информацию о курсе, всех его лекциях в указанном году "
        "и количестве студентов для каждой лекции"
    ),
)
async def get_course_report(
    year: int = Query(2025, description="Год для фильтрации лекций"),
    course_name: str = Query("Базы данных", description="Название курса"),
    service: ReportService = Depends(get_report_service),
) -> CourseReportResponse:
    """
    Эндпоинт для получения отчета по курсу
    
    - **year**: год обучения
    - **course_name**: название курса для поиска
    """
    return await service.get_requirements(course_name, year)


@app.get("/health", summary="Проверка работоспособности")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "service": "Lab2 Python"}
