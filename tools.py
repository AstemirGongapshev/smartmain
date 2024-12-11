from sqlalchemy.orm import Session
from models import User, CreditHistory
from shemas import UserCreate, CreditHistoryCreate
from typing import Optional, List


def create_user(db: Session, user_create: UserCreate) -> User:
    
    existing_user = db.query(User).filter_by(email=user_create.email).first()
    if existing_user:
        raise ValueError("Пользователь с таким email уже существует.")

    user = User(
        name=user_create.name,
        email=user_create.email,
        phone_number=user_create.phone_number,
        password_hash=user_create.password  
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_credit_history(db: Session, user_id: int, credit_history_create: CreditHistoryCreate) -> CreditHistory:

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError("Пользователь не найден.")

    credit_history = CreditHistory(
        user_id=user_id,
        organization=credit_history_create.organization,
        has_credit=credit_history_create.has_credit,
        has_criminal_record=credit_history_create.has_criminal_record,
        is_underage=credit_history_create.is_underage,
        credit_score=credit_history_create.credit_score,
        employment_status=credit_history_create.employment_status,
        monthly_expenses=credit_history_create.monthly_expenses,
        debt_to_income_ratio=credit_history_create.debt_to_income_ratio,
        loan_purpose=credit_history_create.loan_purpose
    )
    db.add(credit_history)
    db.commit()
    db.refresh(credit_history)
    return credit_history


def delete_user_account(db: Session, user_id: int):

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError("Пользователь не найден.")

    db.query(CreditHistory).filter_by(user_id=user_id).delete()
    db.delete(user)
    db.commit()

# 4. Изменение пароля
def update_user_password(db: Session, user_id: int, new_password: str):

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError("Пользователь не найден.")

    user.password_hash = new_password  
    db.commit()
    db.refresh(user)


def get_user_credit_history(db: Session, user_id: int) -> List[CreditHistory]:
    
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError("Пользователь не найден.")

    return db.query(CreditHistory).filter_by(user_id=user_id).all()


def user_exists(db: Session, email: str) -> bool:
    
    return db.query(User).filter_by(email=email).first() is not None
