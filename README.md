# Senior Python Async CRM

Полнофункциональный, production-ready backend для multi-tenant CRM системы на базе асинхронного стека Python. Реализация выполнена в соответствии с требованиями senior-уровня.

## 🚀 Технологический стек

- **Python 3.10+** - современная версия с полной поддержкой type hints
- **FastAPI** - async веб-фреймворк для высокопроизводительных API
- **SQLAlchemy Core** (async) - ORM для работы с базой данных
- **Alembic** - система миграций базы данных
- **PostgreSQL** - реляционная СУБД
- **JWT** - безопасная аутентификация с access/refresh токенами
- **Type hints + mypy/pyright** - статическая типизация
- **Docker + Docker Compose** - контейнеризация
- **pydantic-settings** - управление конфигурацией
- **pytest + httpx** - тестирование API
- **ruff + flake8 + isort** - линтинг и форматирование

## 📋 Ключевые возможности

### Бизнес-логика
- ✅ Multi-tenant архитектура (организации, пользователи, роли)
- ✅ Управление контактами с поиском и фильтрацией
- ✅ Управление сделками (deals) с полным жизненным циклом
- ✅ Задачи (tasks) привязанные к сделкам
- ✅ Лог активности (activities) с автоматическим отслеживанием
- ✅ Аналитика: сводка по сделкам и воронка продаж

### RBAC (Role-Based Access Control)
- **Owner** - полный доступ ко всем ресурсам организации
- **Admin** - управление всеми сделками и контактами
- **Manager** - просмотр и редактирование сделок
- **Member** - доступ только к своим сделкам и контактам

### Технические особенности
- ✅ Полностью асинхронный код
- ✅ Строгая типизация (type hints, mypy)
- ✅ RESTful JSON API v1
- ✅ Автоматическая валидация запросов (Pydantic)
- ✅ JWT аутентификация
- ✅ Миграции базы данных (Alembic)
- ✅ Comprehensive test coverage
- ✅ OpenAPI/Swagger документация
- ✅ Docker ready
- ✅ Production-ready код

## 🏗️ Архитектура

Проект структурирован по слоям:

```
src/
├── api/              # API endpoints (FastAPI routers)
├── services/         # Бизнес-логика
├── repositories/     # Слой работы с БД
├── models/           # ORM модели (SQLAlchemy)
├── schemas/          # Pydantic схемы для валидации
├── config.py         # Конфигурация приложения
├── database.py       # Настройка БД
├── dependencies.py   # FastAPI dependencies (auth, RBAC)
├── security.py       # JWT, хеширование паролей
└── main.py           # Точка входа FastAPI приложения
```

## 📦 Установка и запуск

### Локальная разработка

1. **Клонировать репозиторий:**
```bash
git clone https://github.com/Teketkom/senior-python-crm.git
cd senior-python-crm
```

2. **Создать виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установить зависимости:**
```bash
make install
# или
pip install -r requirements.txt
```

4. **Настроить переменные окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

5. **Запустить PostgreSQL (через Docker):**
```bash
make docker-up
```

6. **Применить миграции:**
```bash
make migrate
```

7. **Запустить сервер:**
```bash
make run
# или
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: `http://localhost:8000`

Документация API: `http://localhost:8000/api/v1/docs`

### Docker Compose (Production-ready)

```bash
# Запустить всё в Docker
docker-compose up -d

# Применить миграции внутри контейнера
docker-compose exec app alembic upgrade head

# Просмотр логов
make docker-logs
```

## 🧪 Тестирование

```bash
# Запустить все тесты
make test

# Запустить конкретный тест
pytest tests/test_auth.py -v

# С покрытием
pytest --cov=src tests/
```

## 🔍 Линтинг и форматирование

```bash
# Проверка кода
make lint

# Автоформатирование
make format
```

## 📚 API Документация

### Аутентификация

**POST /api/v1/auth/register** - Регистрация пользователя и создание организации
```json
{
  "email": "owner@example.com",
  "password": "StrongPassword123",
  "name": "Alice Owner",
  "organization_name": "Acme Inc"
}
```

**POST /api/v1/auth/login** - Вход
```json
{
  "email": "owner@example.com",
  "password": "StrongPassword123"
}
```

**GET /api/v1/auth/me** - Информация о текущем пользователе

**GET /api/v1/auth/organizations/me** - Список организаций пользователя

### Контакты

**GET /api/v1/contacts/** - Список контактов (с фильтрацией и поиском)
- Query параметры: `page`, `page_size`, `search`, `owner_id`
- Headers: `Authorization`, `X-Organization-Id`

**POST /api/v1/contacts/** - Создать контакт
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "123456789"
}
```

### Сделки (Deals)

**GET /api/v1/deals/** - Список сделок
- Фильтры: `status`, `stage`, `min_amount`, `max_amount`, `owner_id`
- Сортировка: `order_by` (created_at, amount), `order` (asc, desc)

**POST /api/v1/deals/** - Создать сделку
```json
{
  "contact_id": 101,
  "title": "Website redesign",
  "amount": "10000.0",
  "currency": "EUR"
}
```

**PATCH /api/v1/deals/{deal_id}** - Обновить сделку
- Автоматически логирует изменения статуса/стадии
- Валидация: won сделки должны иметь amount > 0
- Members не могут менять stage

### Задачи (Tasks)

**GET /api/v1/tasks/** - Список задач
- Фильтры: `deal_id`, `only_open`, `due_before`, `due_after`

**POST /api/v1/tasks/** - Создать задачу
```json
{
  "deal_id": 201,
  "title": "Call client",
  "description": "Discuss proposal",
  "due_date": "2025-01-15T10:00:00"
}
```

**PATCH /api/v1/tasks/{task_id}/mark-done** - Отметить задачу как выполненную

### Активности (Activities)

**GET /api/v1/deals/{deal_id}/activities** - Лог активности сделки

**POST /api/v1/deals/{deal_id}/activities** - Добавить комментарий
```json
{
  "type": "comment",
  "payload": {"text": "Client requested updated proposal"}
}
```

### Аналитика

**GET /api/v1/analytics/deals/summary** - Сводка по сделкам
- Query: `days` (по умолчанию 30)
- Возвращает: количество сделок, сумму, выигранные сделки, средний чек

**GET /api/v1/analytics/deals/funnel** - Воронка продаж (deals по стадиям)

## 🔐 Безопасность

- JWT токены с access/refresh механизмом
- Bcrypt хеширование паролей
- RBAC на уровне API
- Валидация всех входных данных
- Защита от SQL инъекций (parametrized queries)
- CORS настроен

## 📊 База данных

### Модели данных:

1. **Organization** - Организации (multi-tenancy)
2. **User** - Пользователи
3. **OrganizationMember** - Членство в организации с ролями
4. **Contact** - Контакты
5. **Deal** - Сделки (status: new/inprogress/won/lost, stage: qualification/proposal/negotiation/closed)
6. **Task** - Задачи по сделкам
7. **Activity** - Лог активности (comment/statuschanged/taskcreated/system)

### Миграции:

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "Add new feature"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

## 🛠️ Разработка

### Makefile команды:

```bash
make install        # Установить зависимости
make run           # Запустить сервер в dev режиме
make test          # Запустить тесты
make lint          # Проверить код (ruff, mypy)
make format        # Отформатировать код
make migrate       # Применить миграции
make migrate-create msg="message"  # Создать миграцию
make docker-up     # Запустить Docker Compose
make docker-down   # Остановить Docker Compose
make docker-logs   # Логи Docker
```

## 📝 Требования к коду

- ✅ Type hints обязательны для всех функций
- ✅ Docstrings для публичных API
- ✅ Async/await для всех I/O операций
- ✅ Тесты для критичной бизнес-логики
- ✅ Валидация через Pydantic
- ✅ Соответствие PEP 8 (проверка через ruff)
- ✅ Линтинг через mypy/pyright

## 🚀 Production Deployment

1. Настройте `.env` с production значениями
2. Используйте `docker-compose.yml` для деплоя
3. Настройте reverse proxy (nginx/traefik)
4. Включите HTTPS
5. Настройте мониторинг (prometheus/grafana)
6. Регулярные бэкапы PostgreSQL

## 👨‍💻 Автор

**Dmitriy Shalimov**  
Project Manager / Pentester / AI & SOC Expert  
GitHub: [@Teketkom](https://github.com/Teketkom)

## 📄 Лицензия

Private repository - All rights reserved.

---

**Проект выполнен в соответствии со всеми требованиями senior-уровня:**
- ✅ Полная типизация
- ✅ Async/await архитектура
- ✅ RBAC с 4 уровнями доступа
- ✅ Comprehensive тесты
- ✅ Production-ready код
- ✅ Docker/Docker Compose
- ✅ Миграции БД
- ✅ OpenAPI документация
- ✅ Линтинг и форматирование
- ✅ Structured logging
