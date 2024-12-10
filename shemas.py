
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class UserCreate(BaseModel):
    name: str
    password: int

class UserState(BaseModel):
    current_step: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class LoginRequestCreate(BaseModel):
    user_id: int
    amount: float = Field(..., gt=0, description="Сумма кредита должна быть положительной")


class LoginRequest(BaseModel):
    name: str
    password: str



class CreditHistoryCreate(BaseModel):
    organization: str
    has_credit: bool = False
    has_criminal_record: bool = False
    is_underage: bool = False

class CreditHistoryResponse(BaseModel):
    id: int
    organization: str
    has_credit: bool
    has_criminal_record: bool
    is_underage: bool

    class Config:
        orm_mode = True
