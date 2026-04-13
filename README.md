# Асинхронная загрузка персонажей Star Wars

## Запуск

```bash
# 1. Запустить БД
docker-compose up -d

# 2. Создать таблицы
python migrate.py

```

## Очистка таблицы
```bash
python clean_db.py
```
## .env
```.env
POSTGRES_USER=user
POSTGRES_PASSWORD=123
POSTGRES_DB=db_asyncio
POSTGRES_HOST=localhost
POSTGRES_PORT=5431
```