from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.product_service import ProductService
from ..schemas.product import ProductCreate, ProductUpdate, ProductOut
from .deps import get_current_user, require_admin


router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(q: str | None = None, db: Session = Depends(get_db),
                  _=Depends(get_current_user)) -> list[ProductOut]:
    return [ProductOut.model_validate(p) for p in ProductService(db).list(q)]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db),
                _=Depends(get_current_user)) -> ProductOut:
    return ProductOut.model_validate(ProductService(db).get(product_id))


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db),
                   _=Depends(require_admin)) -> ProductOut:
    return ProductOut.model_validate(ProductService(db).create(data))


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db),
                   _=Depends(require_admin)) -> ProductOut:
    return ProductOut.model_validate(ProductService(db).update(product_id, data))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db),
                   _=Depends(require_admin)) -> None:
    ProductService(db).delete(product_id)
