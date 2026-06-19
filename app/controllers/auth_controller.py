"""Контролер автентифікації — публічний (login/register) + /me для перевірки токена."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.auth_service import AuthService
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from .deps import get_current_user
from ..models.user import User


# Префікс /api/auth додасть FastAPI до всіх роутів цього контролера.
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Створити клієнтський акаунт і одразу видати JWT (зручніше для frontend)."""
    service = AuthService(db)
    user = service.register(username=req.username, password=req.password, full_name=req.full_name)
    _, token = service.authenticate(username=req.username, password=req.password)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Звичайний вхід за логіном/паролем. Повертає JWT і дані користувача."""
    service = AuthService(db)
    user, token = service.authenticate(username=req.username, password=req.password)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    """Хто я? — використовується frontend-ом при перезавантаженні сторінки, щоб відновити сесію."""
    return UserOut.model_validate(user)
