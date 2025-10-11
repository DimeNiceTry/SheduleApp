from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth.dependencies import get_current_user

router = APIRouter(tags=["lab3"], dependencies=[Depends(get_current_user)])
_http_client: Optional[httpx.AsyncClient] = None


def configure_http_client(client: httpx.AsyncClient) -> None:
    """Конфигурация HTTP клиента для проксирования запросов к Lab3"""
    global _http_client
    _http_client = client


@router.get("/lab3", summary="Отчет по группе с информацией о посещаемости")
async def proxy_lab3(
    groupName: str = Query("ДО-02-23", description="Название группы")
):
    """
    Проксирует запрос к сервису Lab3 для получения отчета по группе.
    
    Возвращает информацию о:
    - Специальных курсах департамента группы
    - Лекциях этих курсов
    - Студентах группы с общими и посещенными часами
    
    **Требует JWT авторизацию.**
    """
    if _http_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Gateway HTTP client is not ready"
        )
    
    try:
        response = await _http_client.get(
            "/lab3",
            params={
                "groupName": groupName,
            },
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail=f"Lab3 service unavailable: {exc}"
        )
    
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code, 
            detail=response.json()
        )
    
    return response.json()
