from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.auth_service import AuthService
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from .deps import get_current_user
from ..models.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    service = AuthService(db)
    user = service.register(username=req.username, password=req.password, full_name=req.full_name)
    _, token = service.authenticate(username=req.username, password=req.password)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    service = AuthService(db)
    user, token = service.authenticate(username=req.username, password=req.password)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
