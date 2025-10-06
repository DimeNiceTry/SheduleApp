# University Schedule Lab1 Python API

Аналитический сервис для подготовки отчетов о посещаемости студентов. Сервис анализирует данные посещаемости лекций из нескольких баз данных и генерирует отчеты о студентах с наименьшей посещаемостью.

## 🌐 Endpoints

### Health Check
```http
GET /healthz
```
Проверка статуса сервиса.

**Response:**
```json
{
  "status": "ok"
}
```

### Low Attendance Report
```http
GET /lab1?searchTerm={term}&startDate={date}&endDate={date}
```

Возвращает отчет о 10 студентах с наименьшей посещаемостью лекций, соответствующих поисковому запросу в указанный период.

**Parameters:**
- `searchTerm` (required) - Термин или фраза для поиска в материалах лекций (Elasticsearch full-text search)
- `startDate` (required) - Начало отчетного периода (ISO 8601 format: `2025-09-01T00:00:00Z`)
- `endDate` (required) - Конец отчетного периода (ISO 8601 format: `2025-12-31T23:59:59Z`)

**Example Request:**
```bash
curl "http://localhost:8100/lab1?searchTerm=архитектура&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z"
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8100/lab1?searchTerm=архитектура&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z" | ConvertTo-Json -Depth 10
```

**Response:**
```json
{
  "results": [
    {
      "student": {
        "id": 42,
        "full_name": "Иванов Иван Иванович",
        "group_id": 5,
        "date_of_recipient": "2024-09-01T00:00:00Z"
      },
      "attendance_percentage": 45.5,
      "attended_lectures": 10,
      "total_lectures": 22,
      "report_start": "2025-09-01T00:00:00Z",
      "report_end": "2025-12-31T23:59:59Z",
      "search_term": "архитектура"
    }
  ]
}
```

## 🗄️ Data Sources

Сервис использует 4 разные базы данных:

1. **Elasticsearch** (порт 9200)
   - Полнотекстовый поиск по материалам лекций
   - Индекс: `materials`
   - Поля: `id`, `id_lect`, `name`, `lecture_text`

2. **Neo4j** (порт 7687)
   - Графовые связи между лекциями и студентами
   - Узлы: `Student`, `Lecture`, `Course`
   - Связи: `ENROLLED_IN`

3. **PostgreSQL** (порт 5432)
   - Расписание лекций (`Schedules`)
   - Посещения студентов (`Visits`)
   - База данных: `university`

4. **Redis** (порт 6379)
   - Кэш информации о студентах
   - Ключи: `student:{record_book}`
   - Формат: JSON

## 🔧 Configuration

Сервис настраивается через переменные окружения:

```bash
LAB1_POSTGRES_DSN=postgresql://postgres:postgres@postgres:5432/university
LAB1_REDIS_URL=redis://redis:6379/0
LAB1_ELASTIC_URL=http://elasticsearch:9200
LAB1_ELASTIC_INDEX=materials
LAB1_NEO4J_URI=bolt://neo4j:7687
LAB1_NEO4J_USER=neo4j
LAB1_NEO4J_PASSWORD=password
LAB1_REPORT_LIMIT=10
LAB1_ELASTIC_SEARCH_LIMIT=3000
```

## 📊 Response Schema

### LowAttendanceResponse
```json
{
  "results": [LowAttendanceItem]
}
```

### LowAttendanceItem
```json
{
  "student": {
    "id": integer,
    "full_name": string,
    "group_id": integer | null,
    "date_of_recipient": string | null
  },
  "attendance_percentage": float (0-100),
  "attended_lectures": integer (>= 0),
  "total_lectures": integer (>= 0),
  "report_start": string (ISO 8601),
  "report_end": string (ISO 8601),
  "search_term": string
}
```

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "endDate must be greater than startDate"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "searchTerm"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🚀 Usage Examples

### Поиск студентов с низкой посещаемостью лекций по "архитектуре"
```bash
curl "http://localhost:8100/lab1?searchTerm=архитектура&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z"
```

### Поиск по "базам данных" за осенний семестр
```bash
curl "http://localhost:8100/lab1?searchTerm=базы%20данных&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z"
```

### Поиск по "программированию" за весь учебный год
```bash
curl "http://localhost:8100/lab1?searchTerm=программирование&startDate=2025-09-01T00:00:00Z&endDate=2026-06-30T23:59:59Z"
```

## 🧪 Testing

### Healthcheck
```bash
curl http://localhost:8100/healthz
```

### Interactive API Documentation
FastAPI автоматически генерирует интерактивную документацию:

- **Swagger UI:** http://localhost:8100/docs
- **ReDoc:** http://localhost:8100/redoc
- **OpenAPI Schema:** http://localhost:8100/openapi.json

## 📝 Algorithm

1. **Elasticsearch Search** - Находит материалы лекций по поисковому запросу
2. **Neo4j Query** - Получает связанные лекции из графовой БД
3. **PostgreSQL Query** - Извлекает расписание и посещения за период
4. **Calculation** - Вычисляет процент посещаемости для каждого студента
5. **Redis Cache** - Получает информацию о студентах из кэша
6. **Sorting & Limiting** - Сортирует по возрастанию посещаемости, возвращает ТОП-10

## 🔍 Notes

- Максимальное количество результатов в отчете: **10 студентов**
- Лимит поиска в Elasticsearch: **3000 документов**
- Все даты должны быть в формате ISO 8601 с timezone (например: `2025-09-01T00:00:00Z`)
- Поиск в Elasticsearch использует русский анализатор для лучшей работы с кириллицей
- `endDate` должна быть больше `startDate`, иначе вернется ошибка 400

## 🐳 Docker

Сервис запускается как часть docker-compose:

```bash
docker-compose up -d python-lab1
```

Логи:
```bash
docker-compose logs -f python-lab1
```

Перезапуск:
```bash
docker-compose restart python-lab1
```

## 📚 Related Documentation

- OpenAPI Schema: `Схемы/lab1_openapi.json`
- Elasticsearch Schema: `Схемы/elasticsearch.json`
- Neo4j Schema: `Схемы/neo4j.sql`
- PostgreSQL Schema: `Схемы/Postgres.sql`
- Redis Schema: `Схемы/redis.sql`
