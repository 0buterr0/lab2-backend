from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    price: Decimal = Field(ge=Decimal("0"))
    stock: int = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=Decimal("0"))
    stock: int | None = Field(default=None, ge=0)


class ProductOut(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
