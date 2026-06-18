from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic repository — encapsulates session and CRUD primitives.

    Subclasses bind a concrete ORM model and may override methods (polymorphism).
    """

    model: Type[ModelT]

    def __init__(self, db: Session) -> None:
        self._db = db

    @property
    def db(self) -> Session:
        return self._db

    def get(self, entity_id: int) -> ModelT | None:
        return self._db.get(self.model, entity_id)

    def list(self) -> Sequence[ModelT]:
        return self._db.scalars(select(self.model)).all()

    def add(self, entity: ModelT) -> ModelT:
        self._db.add(entity)
        self._db.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self._db.delete(entity)
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()
