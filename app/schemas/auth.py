from pydantic import BaseModel, Field
from ..models.user import UserRole


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class RegisterRequest(LoginRequest):
    full_name: str = Field(default="", max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    is_blacklisted: bool

    model_config = {"from_attributes": True}


TokenResponse.model_rebuild()
