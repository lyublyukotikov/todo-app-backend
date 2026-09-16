# todo-app-backend

Backend для todo-приложения на FastAPI, SQLAlchemy и PostgreSQL.

## Environment

Создать локальный `.env` из шаблона:

```bash
cp .env.example .env
```

Основные переменные:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me
POSTGRES_DB=postgres

CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
```

## Docker

Запуск backend и PostgreSQL:

```bash
docker compose up --build
```

API будет доступен на:

```text
http://localhost:8080
```

Остановить контейнеры:

```bash
docker compose down
```

Удалить контейнеры вместе с данными БД:

```bash
docker compose down -v
```

## API check

```bash
curl http://localhost:8080/tasks
curl http://localhost:8080/categories
```

Создать задачу:

```bash
curl -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"test task"}'
```

## Frontend

Для frontend API base URL:

```text
http://localhost:8080
```

CORS origins настраиваются через `CORS_ALLOW_ORIGINS` в `.env`.
