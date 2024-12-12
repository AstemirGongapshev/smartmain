from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    credit_story: List["CreditHistoryResponse"] = []

    class Config:
        orm_mode = True


class CreditHistoryCreate(BaseModel):
    has_credit: bool
    income: int
    pasport_data: str
    employment_status: str
    loan_purpose: str


class CreditHistoryResponse(BaseModel):
    id: int
    has_credit: bool
    income: int
    pasport_data: str
    employment_status: str
    loan_purpose: str

    class Config:
        orm_mode = True
