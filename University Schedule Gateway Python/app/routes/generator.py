from typing import Optional, Dict, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["generator"], dependencies=[Depends(get_current_user)])
_http_client: Optional[httpx.AsyncClient] = None


def configure_http_client(client: httpx.AsyncClient) -> None:
    """Конфигурация HTTP клиента для проксирования запросов к Generator"""
    global _http_client
    _http_client = client


class GenerateRequest(BaseModel):
    """Запрос на генерацию данных"""
    specialties_count: int = Field(300, alias="SpecialtiesCount")
    university_count: int = Field(3, alias="UniversityCount")
    institution_count: int = Field(30, alias="InstitutionCount")
    department_count: int = Field(300, alias="DepartmentCount")
    group_count: int = Field(100, alias="GroupCount")
    student_count: int = Field(1000, alias="StudentCount")
    course_count: int = Field(100, alias="CourseCount")
    
    class Config:
        populate_by_name = True


@router.get("/pg_test", summary="Проверка PostgreSQL")
async def proxy_postgres_test():
    """
    Проверка подключения к PostgreSQL.
    Возвращает список студентов из БД.
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get("/api/v1/pg_test")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    return response.json()


@router.get("/redis_test", summary="Проверка Redis")
async def proxy_redis_test():
    """
    Проверка подключения к Redis.
    Возвращает данные студента с ID=1.
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get("/api/v1/redis_test")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    return response.json()


@router.get("/mongo_test", summary="Проверка MongoDB")
async def proxy_mongo_test():
    """
    Проверка подключения к MongoDB.
    Возвращает список университетов.
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get("/api/v1/mongo_test")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    # MongoDB возвращает text/plain, парсим как текст
    return {"data": response.text}


@router.get("/neo4j_test", summary="Проверка Neo4j")
async def proxy_neo4j_test():
    """
    Проверка подключения к Neo4j.
    Возвращает первые 25 узлов из графовой БД.
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get("/api/v1/neo4j_test")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    return response.json()


@router.get("/elastic_test", summary="Проверка Elasticsearch")
async def proxy_elastic_test():
    """
    Проверка подключения к Elasticsearch.
    Возвращает все учебные материалы из индекса materials.
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get("/api/v1/elastic_test")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    return response.json()


@router.get("/elastic_search", summary="Поиск в Elasticsearch")
async def proxy_elastic_search(
    q: str = Query(..., description="Поисковый запрос")
):
    """
    Полнотекстовый поиск по учебным материалам.
    Ищет по полям name и lecture_text.
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get(
            "/api/v1/elastic_search",
            params={"q": q}
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    return response.json()


@router.post("/generate", summary="Генерация тестовых данных")
async def proxy_generate(request: GenerateRequest = None):
    """
    Генерирует и сохраняет тестовые данные во все базы данных:
    - PostgreSQL (студенты, курсы, лекции, материалы)
    - MongoDB (группы, университеты)
    - Redis (кэш студентов)
    - Neo4j (граф связей)
    - Elasticsearch (индекс материалов)
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    # Если запрос пустой, используем значения по умолчанию
    if request is None:
        request = GenerateRequest()
    
    try:
        response = await _http_client.post(
            "/generate",
            json=request.model_dump(by_alias=True),
            timeout=300.0  # 5 минут на генерацию
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    return response.json()


@router.delete("/cleanup", summary="Очистка всех баз данных")
async def proxy_cleanup():
    """
    Удаляет все данные из всех баз данных:
    - PostgreSQL
    - MongoDB
    - Redis
    - Neo4j
    - Elasticsearch
    
    ⚠️ **ВНИМАНИЕ: Это действие необратимо!**
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.delete(
            "/cleanup",
            timeout=60.0  # 1 минута на очистку
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generator service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        try:
            detail = response.json()
        except:
            detail = response.text or "Unknown error"
        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    
    return response.json()
