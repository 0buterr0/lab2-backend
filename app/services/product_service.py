import logging
from sqlalchemy.orm import Session

from ..models.product import Product
from ..repositories.product_repository import ProductRepository
from ..schemas.product import ProductCreate, ProductUpdate
from .errors import NotFoundError

log = logging.getLogger(__name__)


class ProductService:
    def __init__(self, db: Session) -> None:
        self._repo = ProductRepository(db)

    def list(self, q: str | None = None) -> list[Product]:
        return self._repo.search(q)

    def get(self, product_id: int) -> Product:
        p = self._repo.get(product_id)
        if not p:
            raise NotFoundError(f"Product {product_id} not found")
        return p

    def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self._repo.add(product)
        self._repo.commit()
        log.info("Created product id=%s name=%s", product.id, product.name)
        return product

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get(product_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        self._repo.commit()
        log.info("Updated product id=%s", product.id)
        return product

    def delete(self, product_id: int) -> None:
        product = self.get(product_id)
        self._repo.delete(product)
        self._repo.commit()
        log.info("Deleted product id=%s", product_id)
