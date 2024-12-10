from sqlalchemy.orm import Session
from models import User, LoginRequest, CreditHistory
from shemas import UserCreate, LoginRequestCreate, UserState, CreditHistoryCreate
from pydantic import ValidationError
from typing import Optional


def validate_login_request(user: User) -> bool:

    if user.active_credit:
        return False
    if user.criminal_record:
        return False
    if user.underage:
        return False
    if user.credit_history:
        return True
    return False


def create_user(db: Session, user_create: UserCreate) -> User:

    existing_user = db.query(User).filter_by(name=user_create.name).first()
    if existing_user:
       
        return existing_user


    user = User(
        name=user_create.name,
        password_hash=user_create.password,  
        credit_history=False,  
        criminal_record=False, 
        underage=False,        
        active_credit=False    
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_login_request(db: Session, login_request_create: LoginRequestCreate) -> LoginRequest:

    login_request = LoginRequest(
        user_id=login_request_create.user_id,
        amount=login_request_create.amount,
        status="pending"
    )
    db.add(login_request)
    db.commit()
    db.refresh(login_request)
    return login_request


def update_user_state(db: Session, user_id: int, new_state: UserState) -> User:

    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.state = new_state.dict()  
        db.commit()
        db.refresh(user)
    return user


def get_user_state(user: User) -> Optional[UserState]:

    if user.state:
        try:
            return UserState(**user.state)  
        except ValidationError:
            return None
    return None


def authenticate_user(db: Session, name: str, password: str) -> Optional[User]:

    user = db.query(User).filter_by(name=name).first()
    if not user:
        return None
    if user.password_hash != password:  
        return None
    return user


def create_credit_history(db: Session, credit_history_create: CreditHistoryCreate, user_id: int) -> CreditHistory:

    credit_history = CreditHistory(
        user_id=user_id,
        organization=credit_history_create.organization,
        has_credit=credit_history_create.has_credit,
        has_criminal_record=credit_history_create.has_criminal_record,
        is_underage=credit_history_create.is_underage
    )
    db.add(credit_history)
    db.commit()
    db.refresh(credit_history)
    return credit_history
