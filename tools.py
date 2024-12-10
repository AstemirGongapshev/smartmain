# smart_bot/tools.py

from sqlalchemy.orm import Session
from models import User, LoginRequest, CreditHistory
from shemas import UserCreate, LoginRequestCreate, UserState, LoginRequest, CreditHistoryCreate
from pydantic import ValidationError
from typing import Optional
from passlib.context import CryptContext

# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Хеширует пароль.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль.
    """
    return pwd_context.verify(plain_password, hashed_password)

def validate_loan_request(user: User) -> bool:
    """
    Проверяет условия для одобрения кредита.
    """
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
    """
    Создает нового пользователя в базе данных.
    """
    existing_user = db.query(User).filter_by(telegram_id=user_create.telegram_id).first()
    if existing_user:
        return existing_user

    hashed_password = hash_password(user_create.password)

    user = User(
        telegram_id=user_create.telegram_id,
        name=user_create.name,
        password_hash=hashed_password,
        credit_history=False,  # По умолчанию
        criminal_record=False, # По умолчанию
        underage=False,        # По умолчанию
        active_credit=False    # По умолчанию
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_login_request(db: Session, login_request_create: LoginRequestCreate) -> LoginRequest:
    """
    Создает новую заявку на кредит.
    """
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
    """
    Обновляет состояние пользователя.
    """
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.state = new_state.dict()
        db.commit()
        db.refresh(user)
    return user

def get_user_state(user: User) -> Optional[UserState]:
    """
    Получает состояние пользователя.
    """
    if user.state:
        try:
            return UserState(**user.state)
        except ValidationError:
            return None
    return None

def authenticate_user(db: Session, telegram_id: str, password: str) -> Optional[User]:
    """
    Аутентифицирует пользователя по Telegram ID и паролю.
    """
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_credit_history(db: Session, credit_history_create: CreditHistoryCreate, user_id: int) -> CreditHistory:
    """
    Создает запись кредитной истории для пользователя.
    """
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
