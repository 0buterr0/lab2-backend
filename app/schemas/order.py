from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from ..models.order import OrderStatus


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1)


class OrderOut(BaseModel):
    id: int
    client_id: int
    status: OrderStatus
    total: Decimal
    created_at: datetime
    items: list[OrderItemOut]
    model_config = ConfigDict(from_attributes=True)
