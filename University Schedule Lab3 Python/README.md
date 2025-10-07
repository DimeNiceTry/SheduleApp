# University Schedule Lab3 Python

Python реализация Lab3 - сервис для получения отчета по группе с информацией о специальных курсах департамента и посещаемости студентов.

## Описание

Сервис анализирует данные из всех баз данных (PostgreSQL, MongoDB, Redis, Neo4j) и формирует комплексный отчет:

- **CourseInfo**: Список специальных курсов департамента и их лекций
- **GroupInfo**: Информация о группе и студентах с подсчетом часов
  - `AllHours`: Всего запланированных часов (количество занятий × 2)
  - `VisitHours`: Посещенных часов для каждого студента (количество посещений × 2)

## Функциональность

### Эндпоинт: GET /lab3

**Параметры запроса:**
- `groupName` (string, default: "ДЕФ-02-24"): Название группы

**Пример запроса:**
```bash
curl "http://localhost:8120/lab3?groupName=ДЕФ-02-24"
```

**Пример ответа:**
```json
{
  "CourseInfo": {
    "courses": [
      {
        "Id": 1,
        "Name": "Базы данных",
        "DepartmentId": 2,
        "SpecialityId": 1,
        "Term": "Осенний"
      }
    ],
    "lectures": [
      {
        "Id": 1,
        "Name": "Введение в SQL",
        "Requirements": true,
        "Year": 2025,
        "CourseId": 1
      }
    ]
  },
  "GroupInfo": {
    "group": {
      "Id": 1,
      "Name": "ДЕФ-02-24",
      "DepartmentId": 2,
      "Year": 2024
    },
    "students": [
      {
        "student": {
          "Id": 1,
          "FullName": "Иванов Иван Иванович",
          "GroupId": 1,
          "DateOfRecipient": "2024-09-01"
        },
        "all_hours": 120,
        "visit_hours": 96
      }
    ]
  }
}
```

**Случай ошибки:**
```json
{
  "CourseInfo": null,
  "GroupInfo": null,
  "Message": "Группа 'НЕСУЩЕСТВУЮЩАЯ' не найдена"
}
```

## Архитектура

### Модели (app/models/lab3_models.py)
- `Student`, `Group`, `Course`, `Lecture`, `Schedule`, `Visit` - базовые модели БД
- `StudentDTO` - студент с часами (all_hours, visit_hours)
- `GroupDTO` - группа со списком студентов
- `CourseDTO` - курсы и лекции
- `GroupReportResponse` - финальный ответ

### Репозитории (app/repositories/)
1. **GroupRepository** (MongoDB): Получение группы по имени
2. **StudentRepository** (Redis): Получение студентов по ID
3. **CourseRepository** (PostgreSQL): Фильтрация курсов по департаменту
4. **LectureRepository** (PostgreSQL + Neo4j): Получение лекций и связей из графа
5. **ScheduleRepository** (PostgreSQL): Расписание занятий
6. **VisitsRepository** (PostgreSQL): Посещения студентов

### Сервис (app/services/group_report_service.py)

**Алгоритм работы:**

1. Найти группу по имени в MongoDB
2. Получить ID студентов и лекций из Neo4j (связи CAN_ATTEND, BELONGS_TO)
3. Найти специальные курсы департамента (фильтр по DepartmentId)
4. Получить лекции для этих курсов
5. Получить расписание (Schedules) для лекций группы
6. Подсчитать общие часы: `len(schedules) × 2`
7. Получить все посещения (Visits) студентов
8. Подсчитать посещенные часы для каждого студента: `len(visits_by_student) × 2`
9. Сформировать ответ с CourseInfo и GroupInfo

### Адаптивная схема

Все репозитории поддерживают как **PascalCase** (C# стиль), так и **snake_case** (Python стиль) схемы таблиц PostgreSQL.

## Зависимости

```txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
motor==3.3.2          # MongoDB async driver
redis==5.0.1          # Redis async client
psycopg[binary]==3.1.16  # PostgreSQL async driver
neo4j==5.16.0         # Neo4j driver
```

## Переменные окружения

```bash
LAB3_MONGO_URI=mongodb://admin:password@mongo:27017/?authSource=admin
LAB3_MONGO_DB=university
LAB3_REDIS_HOST=redis
LAB3_REDIS_PORT=6379
LAB3_POSTGRES_DSN=postgresql://postgres:postgres@postgres:5432/university
LAB3_NEO4J_URI=bolt://neo4j:7687
LAB3_NEO4J_USER=neo4j
LAB3_NEO4J_PASSWORD=password
```

## Интеграция с Gateway

Lab3 интегрирован в Gateway Python с JWT аутентификацией:

```bash
# 1. Получить токен
curl -X POST http://localhost:8200/login \
  -H "Content-Type: application/json" \
  -d '{"name": "admin", "password": "admin123"}'

# 2. Использовать токен для запроса
curl http://localhost:8200/lab3?groupName=ДЕФ-02-24 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Docker

```bash
# Сборка и запуск
docker-compose up --build python-lab3

# Прямой доступ (без JWT)
curl "http://localhost:8120/lab3?groupName=ДЕФ-02-24"

# Через Gateway (с JWT)
curl "http://localhost:8200/lab3?groupName=ДЕФ-02-24" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Swagger UI

Документация доступна по адресу:
- Lab3 напрямую: http://localhost:8120/docs
- Gateway: http://localhost:8200/docs

## Логика подсчета часов

### AllHours (Всего часов)
- Количество занятий в расписании (Schedules) для специальных курсов группы
- Формула: `count(Schedules) × 2`
- Одинаково для всех студентов группы

### VisitHours (Посещенных часов)
- Количество фактических посещений (Visits) каждого студента
- Формула: `count(Visits по StudentId) × 2`
- Индивидуально для каждого студента

### Пример
Если в группе 60 занятий (120 часов), и студент посетил 48 занятий:
```json
{
  "student": {...},
  "all_hours": 120,
  "visit_hours": 96
}
```

## Особенности реализации

1. **Множественные источники данных**: Интеграция 4 разных БД в один запрос
2. **Neo4j граф**: Использование отношений для определения доступных лекций
3. **Фильтрация по департаменту**: Только специальные курсы департамента группы
4. **Адаптивная схема**: Автоопределение PascalCase/snake_case
5. **Детальная статистика**: Индивидуальный подсчет для каждого студента

## Сравнение с C# версией

| Аспект | C# Lab3 | Python Lab3 |
|--------|---------|-------------|
| Framework | ASP.NET Core | FastAPI |
| ORM/Query | Dapper | Нативные драйверы |
| Async | Task/async-await | asyncio/async-await |
| Schema | PascalCase | Adaptive (обе) |
| Port | 8060 | 8120 |
| Response | Идентичная структура | Идентичная структура |

Обе версии полностью функционально эквивалентны и возвращают одинаковые данные.
