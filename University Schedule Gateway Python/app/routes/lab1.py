from datetime import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from ..auth.dependencies import get_current_user

router = APIRouter(tags=["lab1"], dependencies=[Depends(get_current_user)])
_http_client: Optional[httpx.AsyncClient] = None


def configure_http_client(client: httpx.AsyncClient) -> None:
    global _http_client
    _http_client = client


@router.get("/lab1")
async def proxy_lab1(searchTerm: str, startDate: datetime, endDate: datetime):
    if _http_client is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gateway HTTP client is not ready")
    try:
        response = await _http_client.get(
            "/lab1",
            params={
                "searchTerm": searchTerm,
                "startDate": startDate.isoformat(),
                "endDate": endDate.isoformat(),
            },
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Lab1 service unavailable: {exc}")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()
