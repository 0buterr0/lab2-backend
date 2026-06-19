"""Базовий узагальнений репозиторій. Ключове місце для ООП-частини: наслідування + інкапсуляція."""
from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..core.database import Base

# Параметр типу T, обмежений нащадками Base. Дозволяє писати BaseRepository[User] і подібне.
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Узагальнений (generic) репозиторій — реалізує спільні CRUD-операції раз.

    ООП тут:
      * Інкапсуляція  — сесія БД захована в приватному полі _db, назовні віддається через @property.
      * Наслідування  — UserRepository / ProductRepository / OrderRepository / BlacklistRepository
                         успадковують усі стандартні методи (get/list/add/delete/commit) без копіювання.
      * Поліморфізм   — нащадки можуть перевизначати методи або додавати специфічні
                         (наприклад get_by_username у UserRepository).
    """

    # Конкретна ORM-модель, з якою працює репозиторій. Задається нащадком.
    model: Type[ModelT]

    def __init__(self, db: Session) -> None:
        # Приватне поле: ззовні не можна випадково замінити сесію.
        self._db = db

    @property
    def db(self) -> Session:
        """Тільки для читання — інкапсуляція."""
        return self._db

    # --- Базові CRUD-методи, спільні для всіх репозиторіїв ---
    def get(self, entity_id: int) -> ModelT | None:
        """Знайти запис за первинним ключем."""
        return self._db.get(self.model, entity_id)

    def list(self) -> Sequence[ModelT]:
        """Повернути всі записи таблиці."""
        return self._db.scalars(select(self.model)).all()

    def add(self, entity: ModelT) -> ModelT:
        """Додати новий запис у сесію (без явного commit)."""
        self._db.add(entity)
        self._db.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self._db.delete(entity)
        self._db.flush()

    def commit(self) -> None:
        """Зафіксувати транзакцію в БД."""
        self._db.commit()
