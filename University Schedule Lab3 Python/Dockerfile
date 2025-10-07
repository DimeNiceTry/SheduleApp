# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Установка зависимостей
COPY ["University Schedule Lab3 Python/requirements.txt", "requirements.txt"]
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY ["University Schedule Lab3 Python/app", "./app"]

# Переменные окружения по умолчанию
ENV LAB3_MONGO_URI=mongodb://mongo:27017
ENV LAB3_MONGO_DB=university
ENV LAB3_REDIS_HOST=redis
ENV LAB3_REDIS_PORT=6379
ENV LAB3_POSTGRES_DSN=postgresql://postgres:postgres@postgres:5432/university
ENV LAB3_NEO4J_URI=bolt://neo4j:7687
ENV LAB3_NEO4J_USER=neo4j
ENV LAB3_NEO4J_PASSWORD=password

EXPOSE 8120

# Запуск FastAPI через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8120"]
