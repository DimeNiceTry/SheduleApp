from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .dependencies import get_elastic, get_neo4j_driver, get_pg_pool, get_redis, startup, shutdown
from .models.responses import LowAttendanceResponse
from .repositories.elastic_repository import ElasticMaterialsRepository
from .repositories.neo4j_repository import LectureGraphRepository
from .repositories.schedule_repository import ScheduleRepository
from .repositories.student_repository import StudentRepository
from .repositories.visits_repository import VisitsRepository
from .services.report_service import LowAttendanceReportService


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    try:
        yield
    finally:
        await shutdown()


app = FastAPI(
    title="University Schedule Lab1 Python API",
    version="1.0.0",
    description="Analytical service that prepares low attendance reports for students.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:7249", "http://localhost", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

elastic_repo = ElasticMaterialsRepository(get_elastic(), settings.elastic_index)
lecture_repo = LectureGraphRepository(get_neo4j_driver())
schedule_repo = ScheduleRepository(get_pg_pool())
visits_repo = VisitsRepository(get_pg_pool())
student_repo = StudentRepository(get_redis())
report_service = LowAttendanceReportService(
    elastic_repo,
    lecture_repo,
    schedule_repo,
    visits_repo,
    student_repo,
)


@app.get("/healthz", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/lab1",
    response_model=LowAttendanceResponse,
    summary="Retrieve the bottom ten students by lecture attendance",
    tags=["reports"],
)
async def get_low_attendance_report(
    search_term: str = Query(..., alias="searchTerm", description="Term or phrase to match within lecture materials"),
    start_date: datetime = Query(..., alias="startDate", description="Inclusive start of the reporting period"),
    end_date: datetime = Query(..., alias="endDate", description="Inclusive end of the reporting period"),
) -> LowAttendanceResponse:
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="endDate must be greater than startDate")
    results = report_service.get_report(search_term, start_date, end_date)
    return LowAttendanceResponse(results=results)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"message": "University Schedule Lab1 Python service"}
