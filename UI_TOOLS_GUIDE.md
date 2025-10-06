# 🎨 Руководство по UI инструментам

Подробная инструкция по работе с веб-интерфейсами для управления базами данных.

## 📊 Kibana - Elasticsearch UI

**URL:** http://localhost:5601

### Первоначальная настройка

1. Откройте Kibana в браузере
2. Перейдите в **Management** → **Stack Management** → **Index Patterns**
3. Создайте Index Pattern:
   - Name: `materials*`
   - Time field: оставьте пустым (если нет временных полей)
4. Нажмите **Create index pattern**

### Просмотр данных

1. Перейдите в **Analytics** → **Discover**
2. Выберите index pattern `materials*`
3. Вы увидите все учебные материалы с полями:
   - `id` - ID материала
   - `id_lect` - ID лекции
   - `name` - название материала
   - `lecture_text` - текст лекции (с русским анализатором)

### Поиск материалов

В поле поиска Kibana можете использовать:

```
# Поиск по названию
name: "архитектура"

# Поиск по тексту лекции
lecture_text: "программное обеспечение"

# Поиск по ID лекции
id_lect: 5

# Комбинированный поиск
name: "введение" AND lecture_text: "система"
```

### Создание визуализаций

1. **Analytics** → **Visualize Library** → **Create visualization**
2. Выберите тип визуализации:
   - **Bar chart** - распределение материалов по лекциям
   - **Pie chart** - соотношение типов материалов
   - **Data table** - табличное представление
3. Добавьте метрики и агрегации по вашим потребностям

---

## 🗄️ pgAdmin - PostgreSQL UI

**URL:** http://localhost:5050

### Вход в систему

- **Email:** admin@admin.com
- **Password:** admin

### Подключение к серверу PostgreSQL

1. После входа нажмите **Add New Server**
2. Вкладка **General:**
   - Name: `University DB` (любое имя)
3. Вкладка **Connection:**
   - Host: `postgres`
   - Port: `5432`
   - Maintenance database: `university`
   - Username: `postgres`
   - Password: `postgres`
   - ✅ Save password
4. Нажмите **Save**

### Просмотр данных

1. В левой панели разверните:
   - **Servers** → **University DB** → **Databases** → **university** → **Schemas** → **public** → **Tables**
2. Основные таблицы:
   - `Universities` - университеты
   - `Institutes` - институты
   - `Departments` - кафедры
   - `Specialities` - специальности
   - `Groups` - группы
   - `Students` - студенты
   - `Courses` - курсы
   - `Lectures` - лекции
   - `Materials` - учебные материалы
   - `Visits` - посещения
   - `Schedules` - расписание

### Выполнение запросов

1. Правый клик на таблице → **Query Tool**
2. Примеры запросов:

```sql
-- Получить всех студентов
SELECT * FROM "Students" LIMIT 100;

-- Студенты с группами
SELECT s."Name", s."Surname", g."Name" as GroupName
FROM "Students" s
JOIN "Groups" g ON s."GroupId" = g."Id";

-- Курсы с количеством материалов
SELECT c."Name", COUNT(m."Id") as MaterialsCount
FROM "Courses" c
LEFT JOIN "Lectures" l ON l."CourseId" = c."Id"
LEFT JOIN "Materials" m ON m."LectureId" = l."Id"
GROUP BY c."Id", c."Name"
ORDER BY MaterialsCount DESC;

-- Статистика посещаемости
SELECT s."Name", s."Surname", 
       COUNT(v."Id") as VisitsCount
FROM "Students" s
LEFT JOIN "Visits" v ON v."StudentId" = s."Id"
GROUP BY s."Id", s."Name", s."Surname"
ORDER BY VisitsCount DESC
LIMIT 20;
```

---

## 🍃 Mongo Express - MongoDB UI

**URL:** http://localhost:8081

### Вход в систему

- **Username:** admin
- **Password:** admin

### Навигация

1. После входа выберите базу данных `university`
2. Вы увидите коллекции:
   - `groups` - группы студентов
   - Другие коллекции по мере добавления

### Просмотр документов

1. Кликните на коллекцию (например, `groups`)
2. Вы увидите все документы в JSON формате
3. Каждая группа содержит:
   - `_id` - уникальный идентификатор MongoDB
   - `group_id` - ID группы
   - `name` - название группы
   - `speciality` - специальность
   - `students` - массив студентов группы

### Редактирование данных

1. Кликните на иконку **✏️ Edit** рядом с документом
2. Измените JSON
3. Нажмите **Save**

### Добавление нового документа

1. Нажмите **New Document**
2. Введите JSON:

```json
{
  "group_id": 999,
  "name": "ИС-99",
  "speciality": "Информационные системы",
  "students": [
    {
      "student_id": 1001,
      "name": "Иван Иванов",
      "record_book": "РБ-123456"
    }
  ]
}
```

3. Нажмите **Save**

### Поиск документов

Используйте фильтр в формате MongoDB query:

```javascript
// Найти группу по имени
{ "name": "ИС-01" }

// Найти группы специальности
{ "speciality": "Информационные системы" }

// Найти группы с количеством студентов > 20
{ "students.20": { "$exists": true } }
```

---

## 🔴 Redis Commander - Redis UI

**URL:** http://localhost:8082

### Обзор интерфейса

После открытия вы увидите:
- Список всех ключей Redis слева
- Детали выбранного ключа справа

### Просмотр данных студентов

1. В списке ключей ищите ключи формата `student:РБ-XXXXXX`
2. Кликните на ключ чтобы увидеть данные студента
3. Данные хранятся как JSON строки с полями:
   - `record_book` - номер зачетной книжки
   - `name` - имя
   - `surname` - фамилия
   - `group_id` - ID группы
   - `speciality` - специальность

### Поиск ключей

Используйте поле поиска вверху:
- `student:*` - все студенты
- `student:РБ-12*` - студенты с зачеткой начинающейся на РБ-12

### Редактирование значения

1. Кликните на ключ
2. Нажмите **Edit**
3. Измените JSON значение
4. Нажмите **Save**

### Удаление ключа

1. Кликните на ключ
2. Нажмите **Delete**

### CLI команды

В нижней части есть Redis CLI:

```redis
# Получить значение
GET student:РБ-123456

# Получить все ключи студентов
KEYS student:*

# Получить количество ключей
DBSIZE

# Время жизни ключа (TTL)
TTL student:РБ-123456

# Установить время жизни (3600 секунд = 1 час)
EXPIRE student:РБ-123456 3600
```

---

## 🔵 Neo4j Browser

**URL:** http://localhost:7474

### Вход в систему

- **Connect URL:** `bolt://localhost:7687`
- **Username:** neo4j
- **Password:** password

### Обзор графа

После подключения выполните запросы Cypher:

```cypher
// Показать все узлы и связи (ограничено 100)
MATCH (n) RETURN n LIMIT 100

// Показать студентов и их курсы
MATCH (s:Student)-[r:ENROLLED_IN]->(c:Course)
RETURN s, r, c
LIMIT 50

// Найти студента по имени
MATCH (s:Student)
WHERE s.name CONTAINS "Иван"
RETURN s

// Курсы студента
MATCH (s:Student {id: 1})-[:ENROLLED_IN]->(c:Course)
RETURN s.name as Student, c.name as Course

// Студенты на конкретном курсе
MATCH (s:Student)-[:ENROLLED_IN]->(c:Course {name: "Базы данных"})
RETURN s.name, s.surname

// Количество студентов на каждом курсе
MATCH (s:Student)-[:ENROLLED_IN]->(c:Course)
RETURN c.name as Course, COUNT(s) as StudentsCount
ORDER BY StudentsCount DESC

// Найти студентов с общими курсами
MATCH (s1:Student)-[:ENROLLED_IN]->(c:Course)<-[:ENROLLED_IN]-(s2:Student)
WHERE s1.id < s2.id
RETURN s1.name, s2.name, COUNT(c) as CommonCourses
ORDER BY CommonCourses DESC
LIMIT 20
```

### Визуализация

- **Узлы** отображаются как круги разного цвета
- **Связи** отображаются как стрелки
- Кликните на узел чтобы увидеть его свойства
- Используйте колесико мыши для масштабирования
- Перетаскивайте узлы для лучшей визуализации

### Создание данных (пример)

```cypher
// Создать нового студента
CREATE (s:Student {
  id: 9999,
  name: "Петр",
  surname: "Петров",
  record_book: "РБ-999999"
})
RETURN s

// Связать студента с курсом
MATCH (s:Student {id: 9999})
MATCH (c:Course {id: 1})
CREATE (s)-[r:ENROLLED_IN]->(c)
RETURN s, r, c
```

---

## 🔧 Полезные советы

### Резервное копирование

```bash
# PostgreSQL
docker exec postgres pg_dump -U postgres university > backup.sql

# MongoDB
docker exec mongo mongodump --archive > mongo_backup.archive

# Redis
docker exec redis redis-cli SAVE
```

### Мониторинг производительности

- **Kibana**: Monitoring → Stack Monitoring
- **pgAdmin**: Dashboard показывает активность
- **Redis Commander**: Server Info показывает статистику

### Импорт/Экспорт данных

- **pgAdmin**: Tools → Import/Export Data
- **Mongo Express**: Кнопки Import/Export в каждой коллекции
- **Kibana**: Management → Saved Objects

---

## 🚨 Troubleshooting

### Не могу подключиться к UI

```bash
# Проверьте статус контейнеров
docker-compose ps

# Перезапустите конкретный сервис
docker-compose restart [service_name]

# Посмотрите логи
docker-compose logs [service_name]
```

### pgAdmin не видит таблицы

1. Обновите список: Правый клик на Tables → Refresh
2. Проверьте что схема `public` выбрана

### Kibana не показывает данные

1. Проверьте что индекс `materials` существует в Elasticsearch:
   ```bash
   curl http://localhost:9200/_cat/indices
   ```
2. Пересоздайте Index Pattern в Kibana

### Neo4j пустой

Запустите генерацию данных через C# Generator API:
```bash
curl -X POST http://localhost:8000/generate
```
