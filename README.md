# RTU MIREA Schedule API

REST API для получения расписания РТУ МИРЭА. Данные берутся с [schedule-of.mirea.ru](https://schedule-of.mirea.ru) через открытый API (iCal-формат) и отдаются клиенту как чистый JSON.

## Эндпоинты

### Поиск

```
GET /api/search?query={запрос}&limit=15
```

Ищет группы, преподавателей и кабинеты по имени.

**Пример:**
```bash
curl "http://localhost:8000/api/search?query=БСБО-11-23"
```

```json
{
  "data": [
    {
      "id": 708,
      "title": "БСБО-11-23",
      "full_title": "БСБО-11-23",
      "target": 1
    }
  ]
}
```

Значения поля `target`: `1` — группа, `2` — преподаватель, `3` — кабинет.

---

### Расписание

```
GET /api/schedule/{type}/{id}?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
```

Возвращает расписание для группы, преподавателя или кабинета за указанный период.
По умолчанию `date_from` и `date_to` — сегодняшняя дата.

| Параметр       | Описание                                      |
|----------------|-----------------------------------------------|
| `type`         | `1` — группа, `2` — преподаватель, `3` — кабинет |
| `id`           | ID из результатов поиска                      |
| `date_from`    | Начало периода (включительно)                 |
| `date_to`      | Конец периода (включительно)                  |

**Примеры:**
```bash
# Расписание группы за неделю
curl "http://localhost:8000/api/schedule/1/708?date_from=2026-02-23&date_to=2026-03-01"

# Расписание преподавателя на день
curl "http://localhost:8000/api/schedule/2/1909?date_from=2026-02-27&date_to=2026-02-27"

# Расписание кабинета
curl "http://localhost:8000/api/schedule/3/135?date_from=2026-02-27&date_to=2026-02-27"
```

```json
{
  "lessons": [
    {
      "date": "2026-02-24",
      "time_start": "09:00",
      "time_end": "10:30",
      "discipline": "Разработка веб-приложений",
      "lesson_type": "ЛК",
      "lesson_type_full": "Лекции",
      "teachers": [{ "id": 1909, "name": "Потапов Сергей Олегович" }],
      "groups": [{ "id": 708, "name": "БСБО-11-23" }],
      "room": { "id": 135, "number": "145б", "campus": "С-20" }
    }
  ],
  "date_from": "2026-02-24",
  "date_to": "2026-03-01"
}
```

---

### Номер недели

```
GET /api/week
```

```bash
curl "http://localhost:8000/api/week"
```

```json
{
  "weekNumber": 3,
  "schedulePeriodType": "Semester",
  "start": "2026-02-08T21:00:00+00:00",
  "end": "2026-06-14T20:59:59+00:00"
}
```

---

### Документация

OpenAPI-документация доступна по адресу `/schema` после запуска.

## Запуск

### Docker (рекомендуется)

```bash
docker compose up -d
```

API будет доступен на `http://localhost:8000`.

### Локально (uv)

```bash
# Установить зависимости
uv sync

# Запустить
PYTHONPATH=src uv run uvicorn app.main:app --reload
```

## Конфигурация

Переменные окружения (см. `.env.example`):

| Переменная  | По умолчанию | Описание                          |
|-------------|--------------|-----------------------------------|
| `DEBUG`     | `false`      | Подробное логирование             |
| `CACHE_TTL` | `3600`       | TTL кеша iCal-ответов (секунды)   |

## Технологии

- **[Litestar](https://litestar.dev/)** — веб-фреймворк
- **[httpx](https://www.python-httpx.org/)** — асинхронный HTTP-клиент
- **[icalendar](https://icalendar.readthedocs.io/)** + **[recurring-ical-events](https://github.com/niccokunzmann/python-recurring-ical-events)** — парсинг расписания
- **[cachetools](https://cachetools.readthedocs.io/)** — in-memory TTL-кеш
- **[uv](https://docs.astral.sh/uv/)** — управление зависимостями
