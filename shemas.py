from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime

# User models
class UserCreate(BaseModel):
    name: str = Field(..., description="Имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    phone_number: Optional[str] = Field(None, description="Номер телефона пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя")

    @validator("phone_number")
    def validate_phone_number(cls, value):
        if value and not value.isdigit():
            raise ValueError("Номер телефона должен содержать только цифры")
        return value

class UserState(BaseModel):
    current_step: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: Optional[str]
    is_employed: bool
    income_level: Optional[float]
    registration_date: datetime
    is_active: bool

    class Config:
        orm_mode = True

# LoginRequest models
class LoginRequestCreate(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    amount: float = Field(..., gt=0, description="Сумма кредита должна быть положительной")

class LoginRequestResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# CreditHistory models
class CreditHistoryCreate(BaseModel):
    organization: str = Field(..., description="Название организации")
    has_credit: bool = Field(False, description="Есть ли кредит в организации")
    has_criminal_record: bool = Field(False, description="Наличие судимостей")
    is_underage: bool = Field(False, description="Является ли несовершеннолетним")
    credit_score: Optional[float] = Field(None, ge=0, le=1000, description="Кредитный рейтинг (0-1000)")
    employment_status: Optional[str] = Field(None, description="Статус занятости")
    monthly_expenses: Optional[float] = Field(None, ge=0, description="Ежемесячные расходы")
    debt_to_income_ratio: Optional[float] = Field(None, ge=0, le=1, description="Соотношение долгов к доходам")
    loan_purpose: Optional[str] = Field(None, description="Цель кредита")

class CreditHistoryResponse(BaseModel):
    id: int
    user_id: int
    organization: str
    has_credit: bool
    has_criminal_record: bool
    is_underage: bool
    credit_score: Optional[float]
    employment_status: Optional[str]
    monthly_expenses: Optional[float]
    debt_to_income_ratio: Optional[float]
    loan_purpose: Optional[str]

    class Config:
        orm_mode = True
