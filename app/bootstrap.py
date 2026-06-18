"""Seed initial admin and client accounts on first run."""
import logging
from sqlalchemy.orm import Session

from .core.database import SessionLocal
from .repositories.user_repository import UserRepository
from .repositories.product_repository import ProductRepository
from .services.auth_service import AuthService
from .models.user import UserRole
from .models.product import Product
from decimal import Decimal

log = logging.getLogger(__name__)


def seed() -> None:
    db: Session = SessionLocal()
    try:
        users = UserRepository(db)
        if not users.get_by_username("admin"):
            AuthService(db).register(username="admin", password="admin123",
                                     full_name="Administrator", role=UserRole.ADMIN)
        if not users.get_by_username("client"):
            AuthService(db).register(username="client", password="client123",
                                     full_name="Test Client", role=UserRole.CLIENT)

        products = ProductRepository(db)
        if not products.list():
            for sample in [
                Product(name="Notebook Lenovo IdeaPad", description="14\" laptop",
                        price=Decimal("899.00"), stock=10),
                Product(name="Wireless Mouse Logitech", description="Bluetooth mouse",
                        price=Decimal("29.50"), stock=50),
                Product(name="Mechanical Keyboard", description="RGB switches",
                        price=Decimal("120.00"), stock=20),
            ]:
                products.add(sample)
            products.commit()
            log.info("Seeded sample products")
    finally:
        db.close()
