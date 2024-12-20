from sqlalchemy.orm import Session
from DataBase.data_models import User, CreditHistory
from models import UserCreate, CreditHistoryCreate
from typing import Optional, List
# from passlib.hash import bcrypt
from hashlib import sha256
from Secure.utils import encrypt_data
from base_exceptions import UserAlreadyExistsException, UserNotFoundException, EncryptionException
from DataBase.db import get_db





def create_user(db: Session, user_create: UserCreate) -> User:
    existing_user = db.query(User).filter_by(name=user_create.name).first()
    if existing_user:
        raise UserAlreadyExistsException(name=user_create.name)

    hash_password = sha256(user_create.password.encode()).hexdigest()   
    
    user = User(
        name=user_create.name,
        email=user_create.email,
        phone_number=user_create.phone_number,
        password=hash_password  
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_credit_history(db: Session, user_id: int, credit_history_create: CreditHistoryCreate) -> CreditHistory:


    try:
        encrypted_pasport_data = encrypt_data(credit_history_create.pasport_data)
    except Exception as e:
        raise EncryptionException(f"Не удалось зашифровать паспортные данные. Ошибка: {str(e)}")

    credit_history = CreditHistory(
        user_id=user_id,
        has_credit=credit_history_create.has_credit,
        income=credit_history_create.income,
        pasport_data=encrypted_pasport_data,
        employment_status=credit_history_create.employment_status,
        loan_purpose=credit_history_create.loan_purpose
    )

    db.add(credit_history)
    db.commit()
    db.refresh(credit_history)
    return credit_history



def delete_user_account(db: Session, name: int):

    user = db.query(User).filter_by(name=name).first()
    if not user:
        raise ValueError("Пользователь не найден.")

    db.query(CreditHistory).filter_by(name=name).delete()
    db.delete(user)
    db.commit()


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


def user_exists(db, name: str, password:str) -> bool:

    user_name = db.query(User).filter_by(name=name).first()
    password_hash = sha256(password.encode()).hexdigest()
    print(user_name, password_hash)
    user_password_hashed = db.query(User).filter_by(password=password_hash).first()
    return   user_name, user_password_hashed

