"""Контролер чорного списку — повністю адмінський (всі ендпоінти потребують require_admin)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.blacklist_service import BlacklistService
from ..schemas.blacklist import BlacklistCreate, BlacklistOut
from .deps import require_admin


router = APIRouter(prefix="/api/admin/blacklist", tags=["blacklist"])


@router.get("", response_model=list[BlacklistOut])
def list_blacklist(db: Session = Depends(get_db),
                   _=Depends(require_admin)) -> list[BlacklistOut]:
    return [BlacklistOut.model_validate(e) for e in BlacklistService(db).list()]


@router.post("", response_model=BlacklistOut, status_code=status.HTTP_201_CREATED)
def add_to_blacklist(data: BlacklistCreate, db: Session = Depends(get_db),
                     _=Depends(require_admin)) -> BlacklistOut:
    entry = BlacklistService(db).add(data.user_id, data.reason)
    return BlacklistOut.model_validate(entry)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_blacklist(user_id: int, db: Session = Depends(get_db),
                          _=Depends(require_admin)) -> None:
    BlacklistService(db).remove(user_id)
