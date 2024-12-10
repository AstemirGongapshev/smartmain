from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)  
    credit_history = Column(Boolean, default=False)
    criminal_record = Column(Boolean, default=False)
    underage = Column(Boolean, default=False)  
    active_credit = Column(Boolean, default=False)
    state = Column(JSON, nullable=True) 

    login_requests = relationship("LoginRequest", back_populates="user")
    credit_histories = relationship("CreditHistory", back_populates="user") 

class LoginRequest(Base):
    __tablename__ = 'loan_requests'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="login_requests")

class CreditHistory(Base):
    __tablename__ = 'credit_histories'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization = Column(String, nullable=False)
    has_credit = Column(Boolean, default=False)
    has_criminal_record = Column(Boolean, default=False)
    is_underage = Column(Boolean, default=False)

    user = relationship("User", back_populates="credit_histories")
