import logging
from decimal import Decimal
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.order import Order, OrderItem, OrderStatus
from ..repositories.order_repository import OrderRepository
from ..repositories.product_repository import ProductRepository
from ..repositories.blacklist_repository import BlacklistRepository
from ..schemas.order import OrderCreate
from .errors import NotFoundError, ConflictError, ForbiddenError
from .payment import PaymentProcessor, MockPaymentProcessor

log = logging.getLogger(__name__)


class OrderService:
    def __init__(self, db: Session, payment: PaymentProcessor | None = None) -> None:
        self._orders = OrderRepository(db)
        self._products = ProductRepository(db)
        self._blacklist = BlacklistRepository(db)
        self._payment = payment or MockPaymentProcessor()

    def list_for_user(self, user: User) -> list[Order]:
        if user.is_admin:
            return self._orders.list_all()
        return self._orders.list_for_client(user.id)

    def get_for_user(self, order_id: int, user: User) -> Order:
        order = self._orders.get(order_id)
        if not order:
            raise NotFoundError(f"Order {order_id} not found")
        if not user.is_admin and order.client_id != user.id:
            raise ForbiddenError("You do not own this order")
        return order

    def create(self, client: User, data: OrderCreate) -> Order:
        if self._blacklist.get_by_user(client.id):
            raise ForbiddenError("You are blacklisted and cannot place orders")

        order = Order(client_id=client.id, status=OrderStatus.PENDING, total=Decimal("0.00"))
        for line in data.items:
            product = self._products.get(line.product_id)
            if not product:
                raise NotFoundError(f"Product {line.product_id} not found")
            if product.stock < line.quantity:
                raise ConflictError(f"Not enough stock for product '{product.name}'")
            product.stock -= line.quantity
            order.items.append(OrderItem(
                product_id=product.id,
                quantity=line.quantity,
                unit_price=product.price,
            ))
        order.recalculate_total()
        self._orders.add(order)
        self._orders.commit()
        log.info("Created order id=%s client=%s total=%s", order.id, client.username, order.total)
        return order

    def pay(self, order_id: int, client: User) -> Order:
        order = self.get_for_user(order_id, client)
        if order.status == OrderStatus.PAID:
            raise ConflictError("Order is already paid")
        if order.status == OrderStatus.CANCELLED:
            raise ConflictError("Cannot pay a cancelled order")

        ok = self._payment.charge(order_id=order.id, amount=order.total)
        if not ok:
            log.warning("Payment refused order=%s client=%s", order.id, client.username)
            raise ConflictError("Payment refused")

        order.status = OrderStatus.PAID
        self._orders.commit()
        log.info("Paid order id=%s by client=%s", order.id, client.username)
        return order

    def cancel(self, order_id: int, user: User) -> Order:
        order = self.get_for_user(order_id, user)
        if order.status == OrderStatus.PAID:
            raise ConflictError("Cannot cancel a paid order")
        order.status = OrderStatus.CANCELLED
        for item in order.items:
            if item.product is not None:
                item.product.stock += item.quantity
        self._orders.commit()
        log.info("Cancelled order id=%s by user=%s", order.id, user.username)
        return order
