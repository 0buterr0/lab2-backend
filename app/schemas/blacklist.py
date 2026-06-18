from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BlacklistCreate(BaseModel):
    user_id: int
    reason: str = "non-payment"


class BlacklistOut(BaseModel):
    id: int
    user_id: int
    reason: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
