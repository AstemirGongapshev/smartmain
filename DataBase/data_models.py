from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Date
from datetime import datetime
from DataBase.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=True)
    password = Column(String, nullable=False)
    credit_story = relationship("CreditHistory", back_populates="user", cascade="all, delete-orphan")


class CreditHistory(Base):
    __tablename__ = "credit_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    has_credit = Column(Boolean, default=False)
    income = Column(Integer, nullable=False)
    pasport_data = Column(String, nullable=False)
    employment_status = Column(String, nullable=False)
    loan_purpose = Column(String, nullable=False)

    user = relationship("User", back_populates="credit_story")
