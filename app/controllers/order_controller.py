from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.order_service import OrderService
from ..schemas.order import OrderCreate, OrderOut
from .deps import get_current_user, require_client
from ..models.user import User


router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db),
                user: User = Depends(get_current_user)) -> list[OrderOut]:
    return [OrderOut.model_validate(o) for o in OrderService(db).list_for_user(user)]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)) -> OrderOut:
    return OrderOut.model_validate(OrderService(db).get_for_user(order_id, user))


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db),
                 user: User = Depends(require_client)) -> OrderOut:
    return OrderOut.model_validate(OrderService(db).create(user, data))


@router.post("/{order_id}/pay", response_model=OrderOut)
def pay_order(order_id: int, db: Session = Depends(get_db),
              user: User = Depends(require_client)) -> OrderOut:
    return OrderOut.model_validate(OrderService(db).pay(order_id, user))


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)) -> OrderOut:
    return OrderOut.model_validate(OrderService(db).cancel(order_id, user))
