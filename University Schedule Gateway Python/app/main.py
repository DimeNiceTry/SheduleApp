from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db.session import get_pool, init_schema, shutdown_pool
from .routes import auth as auth_routes
from .routes import lab1 as lab1_routes

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = get_pool()
    pool.open()
    init_schema()
    http_client = httpx.AsyncClient(base_url=settings.lab1_service_url, timeout=30.0)
    lab1_routes.configure_http_client(http_client)
    try:
        yield
    finally:
        await http_client.aclose()
        shutdown_pool()


app = FastAPI(
    title="University Schedule Gateway Python API",
    version="1.0.0",
    description="API gateway with JWT authentication and Lab1 proxy routes.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(lab1_routes.router)


@app.get("/healthz", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"message": "University Schedule Gateway Python"}
