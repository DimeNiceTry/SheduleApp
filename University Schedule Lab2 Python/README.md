# University Schedule Lab2 Python

Python-реализация лабораторной работы №2 для системы управления расписанием университета.

## Описание задания

Выполнить запрос к структуре хранения информации о группах учащихся, курсах обучения, лекционной программе и составу лекционных курсов и практических занятий, а также структуре связей между курсами, специальностями, студентами кафедры и данными о посещении студентами занятий, для извлечения отчета по заданной группе учащихся с указанием объема прослушанных часов лекций а также необходимого объема запланированных часов, в рамках всех курсов для каждого студента группы.

Одна лекция равна 2-м академическим часам. В отчет попадают только лекции, которые содержат тег специальной дисциплины кафедры.

## Технологии

- **FastAPI** - веб-фреймворк
- **PostgreSQL** - хранение курсов и лекций
- **Neo4j** - граф связей между группами, студентами и лекциями
- **Pydantic** - валидация данных
- **psycopg3** - драйвер PostgreSQL с пулом подключений
- **neo4j-driver** - асинхронный драйвер Neo4j

## Архитектура

```
app/
├── models/          # Pydantic модели (Course, Lecture, DTO)
├── repositories/    # Слой доступа к данным
│   ├── course_repository.py    # PostgreSQL: получение курсов
│   └── lecture_repository.py   # PostgreSQL + Neo4j: лекции и группы
├── services/        # Бизнес-логика
│   └── report_service.py       # Формирование отчета
├── config.py        # Настройки приложения
├── dependencies.py  # DI контейнер
└── main.py          # FastAPI endpoints
```

## API Endpoints

### `GET /lab2`

Возвращает отчет по курсу: информацию о курсе, всех его лекциях в заданном году и количестве студентов для каждой лекции.

**Query параметры:**
- `year` (int, default=2025) - год обучения
- `courseName` (string, default="Базы данных") - название курса для поиска

**Пример запроса:**
```bash
curl "http://localhost:8110/lab2?year=2025&courseName=Базы%20данных"
```

**Пример ответа:**
```json
{
  "course": {
    "Id": 11,
    "Name": "Базы данных",
    "DepartmentId": 31,
    "SpecialityId": 62,
    "Term": "2025-2026"
  },
  "lectures": [
    {
      "lecture": {
        "Id": 131,
        "Name": "Лекция 1: Введение в базы данных",
        "Requirements": false,
        "Year": 2025,
        "CourseId": 11
      },
      "student_count": 91
    }
  ]
}
```

### `GET /health`

Проверка работоспособности сервиса.

**Пример ответа:**
```json
{
  "status": "ok",
  "service": "Lab2 Python"
}
```

## Переменные окружения

- `LAB2_POSTGRES_DSN` - строка подключения PostgreSQL
- `LAB2_NEO4J_URI` - URI Neo4j (bolt://...)
- `LAB2_NEO4J_USER` - имя пользователя Neo4j
- `LAB2_NEO4J_PASSWORD` - пароль Neo4j

## Docker Compose

Сервис доступен на порту **8110**:

```yaml
python-lab2:
  build:
    context: .
    dockerfile: ./University Schedule Lab2 Python/Dockerfile
  ports:
    - "8110:8080"
  environment:
    LAB2_POSTGRES_DSN: postgresql://postgres:postgres@postgres:5432/university
    LAB2_NEO4J_URI: bolt://neo4j:7687
    LAB2_NEO4J_USER: neo4j
    LAB2_NEO4J_PASSWORD: password
```

## Запуск

```bash
# Сборка и запуск контейнера
docker-compose up -d --build python-lab2

# Проверка логов
docker logs python-lab2

# Тестирование endpoint
curl "http://localhost:8110/lab2"

# Swagger UI
http://localhost:8110/docs
```

## Особенности реализации

1. **Адаптивная схема**: Автоматически определяет PascalCase (Entity Framework) или snake_case таблицы
2. **Асинхронность**: Neo4j запросы выполняются асинхронно через AsyncDriver
3. **Пул подключений**: PostgreSQL использует psycopg_pool для эффективного управления соединениями
4. **ILIKE поиск**: Нечувствительный к регистру поиск курсов по имени
5. **Агрегация данных**: Подсчет студентов по группам через Cypher запросы

## Особенности Neo4j запросов

### Получение групп и студентов для лекции

```cypher
MATCH (l:Lecture {id: $LectureId})
MATCH (g:Group)-[:HAS_LECTURE]->(l)
WITH g
OPTIONAL MATCH (s:Student)-[:BELONGS_TO]->(g)
RETURN g.id AS GroupId, count(s) AS StudentCount
ORDER BY GroupId
```

Этот запрос:
1. Находит лекцию по ID
2. Получает все связанные группы (через `HAS_LECTURE`)
3. Для каждой группы подсчитывает студентов (через `BELONGS_TO`)
4. Возвращает пары (GroupId, StudentCount)

## Swagger UI

Документация API доступна по адресу: http://localhost:8110/docs

Включает:
- Интерактивное тестирование endpoints
- Схемы запросов/ответов
- Описание параметров
- Дефолтные значения для быстрого тестирования
