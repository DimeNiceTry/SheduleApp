from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth.dependencies import get_current_user

router = APIRouter(tags=["lab2"], dependencies=[Depends(get_current_user)])
_http_client: Optional[httpx.AsyncClient] = None


def configure_http_client(client: httpx.AsyncClient) -> None:
    """Конфигурация HTTP клиента для проксирования запросов к Lab2"""
    global _http_client
    _http_client = client


@router.get("/lab2", summary="Отчет по курсу с количеством студентов")
async def proxy_lab2(
    year: int = Query(2025, description="Год обучения"),
    courseName: str = Query("Базы данных", description="Название курса")
):
    """
    Проксирует запрос к сервису Lab2 для получения отчета по курсу.
    
    Возвращает информацию о курсе, всех его лекциях в заданном году 
    и количестве студентов для каждой лекции.
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get(
            "/lab2",
            params={
                "year": year,
                "courseName": courseName,
            },
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail=f"Lab2 service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code, 
            detail=response.json()
        )
    
    return response.json()
