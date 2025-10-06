# Schedule App - University Database Management System

Система для управления университетским расписанием с использованием различных типов баз данных.

## 🚀 Быстрый старт

```bash
docker-compose up -d
```

## 📊 Архитектура

Проект использует следующие базы данных:
- **PostgreSQL** - основная реляционная БД для хранения университетских данных
- **Redis** - кэширование данных студентов
- **MongoDB** - хранение информации о группах
- **Neo4j** - графовая БД для связей между студентами и курсами
- **Elasticsearch** - полнотекстовый поиск по учебным материалам

## 🌐 API Endpoints

### Основные сервисы

| Сервис | URL | Описание |
|--------|-----|----------|
| **C# Generator** | http://localhost:8000 | Генератор тестовых данных |
| **Python Lab1** | http://localhost:8100 | Отчет о студентах с низкой посещаемостью |
| **Python Lab2** | http://localhost:8110 | Отчет по курсам и лекциям с количеством студентов |
| **Python Gateway** | http://localhost:8200 | API Gateway с аутентификацией |
| **Swagger (Gateway)** | http://localhost:8200/docs | Документация API Gateway |

### C# Generator API

**Swagger:** http://localhost:8000/swagger/index.html

**Основные эндпоинты:**
- `POST /generate` - Генерация тестовых данных
- `DELETE /cleanup` - Удаление всех данных из всех БД
- `GET /elastic_test` - Проверка данных в Elasticsearch
- `GET /elastic_search?q={term}` - Поиск по материалам

### Python Lab1 API

**Swagger:** http://localhost:8100/docs  
**Документация:** [Lab1 README](University%20Schedule%20Lab1%20Python/README.md)  
**OpenAPI Schema:** [lab1_openapi.json](Схемы/lab1_openapi.json)

**Основные эндпоинты:**
- `GET /lab1?searchTerm={term}&startDate={date}&endDate={date}` - Отчет о студентах с низкой посещаемостью
- `GET /healthz` - Проверка здоровья сервиса

**Пример запроса:**
```bash
curl "http://localhost:8100/lab1?searchTerm=архитектура&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z"
```

### Python Lab2 API

**Swagger:** http://localhost:8110/docs  
**Документация:** [Lab2 README](University%20Schedule%20Lab2%20Python/README.md)

**Основные эндпоинты:**
- `GET /lab2?year={year}&courseName={name}` - Отчет по курсу с количеством студентов на лекциях
- `GET /health` - Проверка здоровья сервиса

**Пример запроса:**
```bash
curl "http://localhost:8110/lab2?year=2025&courseName=Базы%20данных"
```

**Описание:** Возвращает информацию о курсе, всех его лекциях в заданном году и количестве студентов для каждой лекции. Использует PostgreSQL для получения курсов и лекций, Neo4j для подсчета студентов по группам.

### API Gateway

**Swagger:** http://localhost:8200/docs - интерфейс с запросами для регистрации и логина по токену

**Примечание:** Регистрация в процессе отладки

## 🎨 UI Инструменты для работы с базами данных

### Kibana (Elasticsearch)
- **URL:** http://localhost:5601
- **Описание:** Визуализация и анализ данных из Elasticsearch
- **Индекс:** `materials` - учебные материалы лекций

### pgAdmin (PostgreSQL)
- **URL:** http://localhost:5050
- **Email:** admin@admin.com
- **Password:** admin
- **Подключение к БД:**
  - Host: `postgres`
  - Port: `5432`
  - Database: `university`
  - Username: `postgres`
  - Password: `postgres`

### Mongo Express (MongoDB)
- **URL:** http://localhost:8081
- **Username:** admin
- **Password:** admin
- **БД:** `university`

### Redis Commander (Redis)
- **URL:** http://localhost:8082
- **Описание:** Просмотр и редактирование данных Redis (кэш студентов)

### Neo4j Browser
- **URL:** http://localhost:7474
- **Username:** neo4j
- **Password:** password
- **Описание:** Графовая визуализация связей студентов и курсов

## 🔧 Генерация данных

### C# Generator API

#### Генерация данных

```bash
# POST http://localhost:8000/generate
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "specialtiesCount": 5,
    "universityCount": 2,
    "institutionCount": 3,
    "departmentCount": 5,
    "groupCount": 10,
    "studentCount": 100,
    "courseCount": 20
  }'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/generate" `
  -ContentType "application/json" `
  -Body '{"specialtiesCount":5,"universityCount":2,"institutionCount":3,"departmentCount":5,"groupCount":10,"studentCount":100,"courseCount":20}'
```

#### Очистка всех данных

```bash
# DELETE http://localhost:8000/cleanup
curl -X DELETE http://localhost:8000/cleanup
```

**PowerShell:**
```powershell
Invoke-RestMethod -Method DELETE -Uri "http://localhost:8000/cleanup"
```

**Результат:**
- Удаляет все данные из PostgreSQL (все таблицы)
- Очищает все ключи Redis
- Удаляет все документы из MongoDB
- Удаляет все узлы и связи из Neo4j
- Удаляет индекс materials из Elasticsearch
- Сбрасывает счётчики автоинкремента в PostgreSQL

### Проверка Elasticsearch данных

```bash
# GET http://localhost:8000/elastic_test
curl http://localhost:8000/elastic_test

# Поиск по материалам
curl "http://localhost:8000/elastic_search?q=архитектура"
```

## 📋 Структура проекта

```
SheduleApp/
├── University Schedule Generator/    # C# генератор данных
├── University Schedule Lab1/         # C# сервис отчетов
├── University Schedule Lab1 Python/  # Python сервис аналитики
├── University Schedule Gateway Python/ # Python API Gateway
├── db/                               # Python модули для работы с БД
├── logs/                             # Логи всех сервисов
├── Схемы/                            # Схемы баз данных
└── docker-compose.yml               # Конфигурация Docker
```

## 🗄️ Порты сервисов

| Сервис | Порт | Протокол |
|--------|------|----------|
| C# Generator | 8000 | HTTP |
| Python Lab1 | 8100 | HTTP |
| Python Gateway | 8200 | HTTP |
| PostgreSQL | 5432 | TCP |
| pgAdmin | 5050 | HTTP |
| Redis | 6379 | TCP |
| Redis Commander | 8082 | HTTP |
| MongoDB | 27017 | TCP |
| Mongo Express | 8081 | HTTP |
| Neo4j (HTTP) | 7474 | HTTP |
| Neo4j (Bolt) | 7687 | Bolt |
| Elasticsearch | 9200 | HTTP |
| Kibana | 5601 | HTTP |

## 🔍 Troubleshooting

### Проблема: Elasticsearch возвращает пустой массив

**Решение:** Убедитесь что данные были сгенерированы через `/generate` endpoint. Индекс `materials` создается автоматически при первом сохранении данных с правильным mapping для русского языка.

### Проверка статуса сервисов

```bash
docker-compose ps
```

### Просмотр логов

```bash
docker-compose logs -f [service_name]
```

## 📝 Примечания

- Все UI инструменты доступны после запуска `docker-compose up -d`
- Данные сохраняются в Docker volumes и не удаляются при перезапуске контейнеров
- Для полной очистки данных: `docker-compose down -v`
