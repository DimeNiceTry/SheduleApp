# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY ["University Schedule Gateway Python/requirements.txt", "requirements.txt"]
RUN pip install --no-cache-dir -r requirements.txt

COPY ["University Schedule Gateway Python/app", "./app"]

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
