# JWT Авторизация - Руководство по тестированию

## 📋 Описание системы

API Gateway реализует JWT (JSON Web Token) авторизацию для защищенного доступа к лабораторным работам. Все запросы к защищенным endpoints требуют валидный JWT токен.

## 🏗️ Архитектура

```
┌─────────┐      ┌──────────────────┐      ┌──────────┐
│ Клиент  │─────▶│  Python Gateway  │─────▶│  Lab1    │
│         │      │  (JWT Auth)      │      │  Service │
└─────────┘      └──────────────────┘      └──────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ PostgreSQL  │
                  │ gateway_auth│
                  └─────────────┘
```

## 🔐 Компоненты безопасности

### 1. База данных `gateway_auth`

**Таблица `users`:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
```

### 2. Хеширование паролей

- **Алгоритм:** bcrypt
- **Библиотека:** `bcrypt==4.1.2`
- **Соль:** Генерируется автоматически при каждом хешировании
- **Раунды:** 12 (по умолчанию bcrypt)

### 3. JWT токены

- **Алгоритм подписи:** HS256 (HMAC-SHA256)
- **Секретный ключ:** Задается в переменной окружения `GATEWAY_JWT_SECRET`
- **Время жизни:** 12 часов (настраивается через `GATEWAY_JWT_EXPIRE_HOURS`)
- **Payload структура:**
  ```json
  {
    "sub": "user_id",
    "exp": 1759828559
  }
  ```

## 🧪 Пошаговое тестирование

### Шаг 0: Проверка работоспособности Gateway

```powershell
Invoke-RestMethod "http://localhost:8200/healthz"
```

**Ожидаемый результат:**
```json
{
  "status": "ok"
}
```

---

### Шаг 1: Регистрация пользователя

**Endpoint:** `POST /register`

**Запрос:**
```powershell
$body = @{
    name = "testuser"
    password = "testpass123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8200/register" `
                  -Method POST `
                  -Body $body `
                  -ContentType "application/json"
```

**Ожидаемый результат:**
```json
{
  "status": "ok"
}
```

**Коды ответов:**
- `201 Created` - пользователь успешно зарегистрирован
- `409 Conflict` - пользователь с таким именем уже существует

---

### Шаг 2: Вход и получение JWT токена

**Endpoint:** `POST /login`

**Запрос:**
```powershell
$body = @{
    name = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8200/login" `
                               -Method POST `
                               -Body $body `
                               -ContentType "application/json"

$token = ($response.Content | ConvertFrom-Json).access_token
Write-Host "JWT Token: $token"
```

**Ожидаемый результат:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Cookie:**
Токен также устанавливается в HTTP-only cookie `access_token` для использования в браузере.

**Коды ответов:**
- `200 OK` - успешная аутентификация
- `401 Unauthorized` - неверные учетные данные

---

### Шаг 3: Попытка доступа БЕЗ токена

**Endpoint:** `GET /lab1`

**Запрос:**
```powershell
try {
    Invoke-RestMethod "http://localhost:8200/lab1?searchTerm=архитектура&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z"
} catch {
    Write-Host "Ошибка (ожидается 401): $($_.Exception.Message)"
}
```

**Ожидаемый результат:**
```
HTTP 401 Unauthorized
{
  "detail": "Missing credentials"
}
```

---

### Шаг 4: Доступ С валидным токеном

**Запрос:**
```powershell
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

$headers = @{
    Authorization = "Bearer $token"
}

$result = Invoke-RestMethod "http://localhost:8200/lab1?searchTerm=код&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z" `
                             -Headers $headers

$result | ConvertTo-Json -Depth 3
```

**Ожидаемый результат:**
```json
{
  "results": [
    {
      "student": {
        "id": 2,
        "full_name": "Дмитрий Сергеевич Сазонов",
        "group_id": 4,
        "date_of_recipient": "2022-09-01"
      },
      "attendance_percentage": 0.0,
      "attended_lectures": 0,
      "total_lectures": 0,
      "report_start": "2025-09-01T00:00:00+00:00",
      "report_end": "2025-12-31T23:59:59+00:00",
      "search_term": "код"
    }
    // ... больше студентов
  ]
}
```

---

## 🔍 Проверка токена

### Декодирование JWT (без проверки подписи)

```powershell
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU5ODI4NTU5fQ.zSZSkFgSlriuKcIu33vwxaf4P6hKiKHLpQJ-qmiyNMI"

# Извлекаем payload (вторая часть между точками)
$parts = $token.Split('.')
$payload = $parts[1]

# Добавляем padding если нужно
while ($payload.Length % 4) {
    $payload += "="
}

# Декодируем из Base64
$bytes = [Convert]::FromBase64String($payload)
$json = [System.Text.Encoding]::UTF8.GetString($bytes)
$json | ConvertFrom-Json
```

**Результат:**
```json
{
  "sub": "1",
  "exp": 1759828559
}
```

- `sub` - ID пользователя (user_id из БД)
- `exp` - Unix timestamp истечения токена

---

## 📊 Таблица endpoints

| Endpoint | Метод | Авторизация | Описание |
|----------|-------|-------------|----------|
| `/healthz` | GET | ❌ Нет | Проверка работоспособности |
| `/register` | POST | ❌ Нет | Регистрация пользователя |
| `/login` | POST | ❌ Нет | Вход и получение токена |
| `/lab1` | GET | ✅ **JWT** | Отчет о студентах с низкой посещаемостью (проксирует в Lab1) |

---

## 🛡️ Безопасность

### Хеширование паролей

```python
import bcrypt

# Хеширование
password = "testpass123"
password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt)

# Проверка
is_valid = bcrypt.checkpw(password_bytes, hashed)
```

### Создание JWT токена

```python
from jose import jwt
from datetime import datetime, timedelta, timezone

payload = {
    "sub": "1",  # User ID
    "exp": datetime.now(timezone.utc) + timedelta(hours=12)
}

token = jwt.encode(payload, "secret_key", algorithm="HS256")
```

### Проверка JWT токена

```python
from jose import jwt, JWTError

try:
    payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
    user_id = payload.get("sub")
except JWTError:
    # Токен невалидный или истек
    user_id = None
```

---

## 🧰 Инструменты для тестирования

### 1. PowerShell (Windows)

Все примеры выше используют PowerShell.

### 2. cURL

```bash
# Регистрация
curl -X POST http://localhost:8200/register \
     -H "Content-Type: application/json" \
     -d '{"name":"testuser","password":"testpass123"}'

# Вход
curl -X POST http://localhost:8200/login \
     -H "Content-Type: application/json" \
     -d '{"name":"testuser","password":"testpass123"}'

# Запрос с токеном
curl -X GET "http://localhost:8200/lab1?searchTerm=код&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Postman

1. **Регистрация:**
   - Method: `POST`
   - URL: `http://localhost:8200/register`
   - Body (JSON):
     ```json
     {
       "name": "testuser",
       "password": "testpass123"
     }
     ```

2. **Вход:**
   - Method: `POST`
   - URL: `http://localhost:8200/login`
   - Body (JSON):
     ```json
     {
       "name": "testuser",
       "password": "testpass123"
     }
     ```
   - Сохраните `access_token` из ответа

3. **Запрос к Lab1:**
   - Method: `GET`
   - URL: `http://localhost:8200/lab1?searchTerm=код&startDate=2025-09-01T00:00:00Z&endDate=2025-12-31T23:59:59Z`
   - Headers:
     - `Authorization`: `Bearer YOUR_TOKEN`

### 4. Swagger UI

Gateway предоставляет Swagger UI на http://localhost:8200/docs

**Порядок действий:**
1. Откройте http://localhost:8200/docs
2. Найдите endpoint `/register` → попробуйте зарегистрироваться
3. Найдите endpoint `/login` → получите токен
4. Нажмите кнопку **Authorize** (замок) вверху страницы
5. Введите `Bearer YOUR_TOKEN`
6. Теперь можете тестировать защищенные endpoints

---

## ⚙️ Переменные окружения

```yaml
GATEWAY_POSTGRES_DSN: postgresql://postgres:postgres@postgres:5432/gateway_auth
GATEWAY_JWT_SECRET: )wmbpam3f%_qe_kg*no-+^nc2dzz(z@d-ijc1mt&ua5^mb&mb+
GATEWAY_JWT_EXPIRE_HOURS: "12"
GATEWAY_LAB1_SERVICE_URL: http://python-lab1:8080
```

---

## 🐛 Типичные ошибки

### 1. `401 Unauthorized: Missing credentials`
- **Причина:** Не передан заголовок `Authorization`
- **Решение:** Добавьте `Authorization: Bearer YOUR_TOKEN`

### 2. `401 Unauthorized: Invalid or expired token`
- **Причина:** Токен истек (прошло >12 часов) или невалиден
- **Решение:** Выполните повторный вход через `/login`

### 3. `409 Conflict: User already exists`
- **Причина:** Пользователь с таким именем уже зарегистрирован
- **Решение:** Используйте другое имя или выполните вход

### 4. `502 Bad Gateway: Lab1 service unavailable`
- **Причина:** Сервис Lab1 не запущен или недоступен
- **Решение:** Проверьте статус контейнера `python-lab1`

---

## 📝 Результаты тестирования

### Успешный сценарий

| Шаг | Действие | Результат | Статус |
|-----|----------|-----------|--------|
| 0 | Проверка healthz | `{"status": "ok"}` | ✅ |
| 1 | Регистрация testuser | `{"status": "ok"}` | ✅ |
| 2 | Вход testuser | Получен JWT токен | ✅ |
| 3 | Запрос без токена | `401 Unauthorized` | ✅ |
| 4 | Запрос с токеном | Получены данные Lab1 | ✅ |

### Проверка безопасности

| Проверка | Результат | Статус |
|----------|-----------|--------|
| Пароли хешируются bcrypt | ✅ | Да |
| Токены подписаны HS256 | ✅ | Да |
| Без токена доступ запрещен | ✅ | Да |
| С истекшим токеном доступ запрещен | ✅ | Да |
| Токены имеют срок действия | ✅ | 12 часов |

---

## 🔗 Swagger UI

**URL:** http://localhost:8200/docs

Интерактивная документация API с возможностью:
- Просмотра всех endpoints
- Тестирования запросов
- Авторизации через UI
- Просмотра схем запросов/ответов

---

## 📚 Дополнительные материалы

- [JWT.io](https://jwt.io) - декодер JWT токенов
- [bcrypt](https://pypi.org/project/bcrypt/) - документация bcrypt
- [python-jose](https://python-jose.readthedocs.io/) - JWT для Python
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) - документация FastAPI
