from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    is_employed = Column(Boolean, default=False)  
    income_level = Column(Float, nullable=True)  
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  
    credit_history = Column(Boolean, default=False)
    criminal_record = Column(Boolean, default=False)
    underage = Column(Boolean, default=False)
    active_credit = Column(Boolean, default=False)
    state = Column(JSON, nullable=True)
    credit_histories = relationship("CreditHistory", back_populates="user")



class CreditHistory(Base):
    __tablename__ = 'credit_histories'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization = Column(String, nullable=False)
    has_credit = Column(Boolean, default=False)
    has_criminal_record = Column(Boolean, default=False)
    is_underage = Column(Boolean, default=False)
    credit_score = Column(Float, nullable=True)  # Кредитный рейтинг
    employment_status = Column(String, nullable=True)  # Статус занятости
    monthly_expenses = Column(Float, nullable=True)  # Ежемесячные расходы
    debt_to_income_ratio = Column(Float, nullable=True)  # Соотношение долгов к доходам
    loan_purpose = Column(String, nullable=True)  # Цель кредита

    user = relationship("User", back_populates="credit_histories")
