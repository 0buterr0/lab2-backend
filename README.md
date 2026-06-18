# lab2 — backend (FastAPI + SQLAlchemy + Alembic + JWT)

REST API для Інтернет-магазину (варіант 9).

## Реалізовано згідно з умовами
- **Менеджер пакетів:** `pip` (`requirements.txt`).
- **Routing / Front Controller:** FastAPI `APIRouter`, окремий controller на кожний домен.
- **MVC:** controllers (`app/controllers`) → services (`app/services`) → repositories (`app/repositories`) → models (`app/models`). View — JSON через Pydantic-схеми.
- **ORM + SQL:** SQLAlchemy 2.x, SQLite (`data/store.db`).
- **Schema Migrations:** Alembic (`alembic/`, файл версії в `alembic/versions/`).
- **JWT-аутентифікація:** `python-jose` + `bcrypt`. Захищені ендпоінти через `Depends(get_current_user)` / `require_admin` / `require_client`.
- **ООП:** наслідування (`BaseRepository[T]`, `TimestampMixin`), поліморфізм (`PaymentProcessor` → `MockPaymentProcessor` / `AlwaysFailingProcessor`), інкапсуляція (приватний `_db` у репозиторіях).
- **Логування:** rotating file + console (`app/core/logging.py`), лог у `logs/app.log`.
- **Unit-тести:** `pytest`, 14 тестів покривають auth/products/orders/blacklist/payment.

## Запуск

```powershell
cd lab2/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# (опційно) Alembic — інакше схема створюється при старті
python -m alembic upgrade head

uvicorn app.main:app --reload
```

API: <http://127.0.0.1:8000>  ·  Swagger: <http://127.0.0.1:8000/docs>

## Тестові акаунти (seed на першому старті)

| Логін   | Пароль    | Роль   |
|---------|-----------|--------|
| admin   | admin123  | admin  |
| client  | client123 | client |

## Тести

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Ендпоінти

| Метод | Шлях                              | Доступ  |
|-------|-----------------------------------|---------|
| POST  | `/api/auth/register`              | публ.   |
| POST  | `/api/auth/login`                 | публ.   |
| GET   | `/api/auth/me`                    | auth    |
| GET   | `/api/products`                   | auth    |
| GET   | `/api/products/{id}`              | auth    |
| POST  | `/api/products`                   | admin   |
| PUT   | `/api/products/{id}`              | admin   |
| DELETE| `/api/products/{id}`              | admin   |
| GET   | `/api/orders`                     | auth    |
| GET   | `/api/orders/{id}`                | auth    |
| POST  | `/api/orders`                     | client  |
| POST  | `/api/orders/{id}/pay`            | client  |
| POST  | `/api/orders/{id}/cancel`         | auth    |
| GET   | `/api/admin/blacklist`            | admin   |
| POST  | `/api/admin/blacklist`            | admin   |
| DELETE| `/api/admin/blacklist/{user_id}`  | admin   |

## Alembic — створити нову міграцію

```powershell
python -m alembic revision --autogenerate -m "опис змін"
python -m alembic upgrade head
```
