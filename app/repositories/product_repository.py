from sqlalchemy import select
from .base import BaseRepository
from ..models.product import Product


class ProductRepository(BaseRepository[Product]):
    model = Product

    def search(self, q: str | None) -> list[Product]:
        stmt = select(Product)
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(Product.name.ilike(like))
        stmt = stmt.order_by(Product.name)
        return list(self._db.scalars(stmt).all())
