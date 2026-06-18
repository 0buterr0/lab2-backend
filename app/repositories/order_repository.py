from sqlalchemy import select
from .base import BaseRepository
from ..models.order import Order


class OrderRepository(BaseRepository[Order]):
    model = Order

    def list_for_client(self, client_id: int) -> list[Order]:
        stmt = select(Order).where(Order.client_id == client_id).order_by(Order.created_at.desc())
        return list(self._db.scalars(stmt).all())

    def list_all(self) -> list[Order]:
        return list(self._db.scalars(select(Order).order_by(Order.created_at.desc())).all())
