FROM python:3.11-slim-bullseye

# Задаем стабильное зеркало (можно заменить на другое, например mirror.yandex.ru)
RUN sed -i 's|deb.debian.org|mirror.yandex.ru|g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       gcc \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Запуск FastAPI через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
