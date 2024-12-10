# smart_bot/bot.py

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from db import init_db, get_db
from tools import (
    create_user,
    validate_loan_request,
    create_credit_history,
    update_user_state,
    get_user_state,
    create_login_request,
    authenticate_user,
    create_credit_history
)
from shemas import UserCreate, LoginRequestCreate, UserState, LoginRequest, CreditHistoryCreate
from models import User
from sqlalchemy.orm import Session

# Установите токен бота вручную
BOT_TOKEN = "8072664742:AAG257f9Dxsz4yG2VdOoPi8UFtCTZEYfJWg"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
def initialize_database():
    init_db()

start_keyboard = [['Зарегистрироваться', 'Войти'], ['Добавить кредитную историю']]
start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /start: Показать кнопки регистрации и входа.
    """
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=start_markup
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса регистрации.
    """
    await update.message.reply_text(
        "Начинаем регистрацию.\nВведите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data['state'] = 'register_name'

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса входа.
    """
    await update.message.reply_text(
        "Вход.\nВведите ваш Telegram ID:",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data['state'] = 'login_id'

async def add_credit_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса добавления кредитной истории.
    """
    with get_db() as db:
        user = db.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()

        if not user:
            await update.message.reply_text("Вы не зарегистрированы! Используйте /start для регистрации.")
            return

        await update.message.reply_text(
            "Начинаем добавление кредитной истории.\nВведите название организации:",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['state'] = 'add_credit_history_organization'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка сообщений пользователя в зависимости от текущего состояния.
    """
    user_state = context.user_data.get('state')
    text = update.message.text.strip()

    if user_state == 'register_name':
        context.user_data['name'] = text
        await update.message.reply_text("Введите пароль:")
        context.user_data['state'] = 'register_password'

    elif user_state == 'register_password':
        context.user_data['password'] = text
        await update.message.reply_text("Введите ваш Telegram ID (числовой):")
        context.user_data['state'] = 'register_id'

    elif user_state == 'register_id':
        telegram_id = text
        if not telegram_id.isdigit():
            await update.message.reply_text("Telegram ID должен быть числом. Повторите ввод Telegram ID:")
            return
        name = context.user_data.get('name')
        password = context.user_data.get('password')
        user_create = UserCreate(
            telegram_id=telegram_id,
            name=name,
            password=password
        )
        with get_db() as db:
            try:
                user = create_user(db, user_create)
                await update.message.reply_text(
                    f"Поздравляем, {user.name}! Вы успешно зарегистрированы.",
                    reply_markup=start_markup
                )
            except Exception as e:
                logger.error(f"Ошибка при регистрации пользователя: {e}")
                await update.message.reply_text("Произошла ошибка при регистрации. Попробуйте снова.")
        context.user_data.clear()

    elif user_state == 'login_id':
        telegram_id = text
        context.user_data['login_id'] = telegram_id
        await update.message.reply_text("Введите пароль:")
        context.user_data['state'] = 'login_password'

    elif user_state == 'login_password':
        password = text
        telegram_id = context.user_data.get('login_id')
        with get_db() as db:
            user = authenticate_user(db, telegram_id, password)
            if user:
                await update.message.reply_text(
                    f"Добро пожаловать, {user.name}!",
                    reply_markup=start_markup
                )
            else:
                await update.message.reply_text(
                    "Неверный Telegram ID или пароль. Попробуйте снова.",
                    reply_markup=start_markup
                )
        context.user_data.clear()

    elif user_state == 'add_credit_history_organization':
        context.user_data['organization'] = text
        await update.message.reply_text("Есть ли у вас кредиты в этой организации? (да/нет)")
        context.user_data['state'] = 'add_credit_history_has_credit'

    elif user_state == 'add_credit_history_has_credit':
        response = text.lower()
        if response in ["да", "yes"]:
            context.user_data['has_credit'] = True
        elif response in ["нет", "no"]:
            context.user_data['has_credit'] = False
        else:
            await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет':")
            return
        await update.message.reply_text("Есть ли у вас судимости? (да/нет)")
        context.user_data['state'] = 'add_credit_history_has_criminal_record'

    elif user_state == 'add_credit_history_has_criminal_record':
        response = text.lower()
        if response in ["да", "yes"]:
            context.user_data['has_criminal_record'] = True
        elif response in ["нет", "no"]:
            context.user_data['has_criminal_record'] = False
        else:
            await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет':")
            return
        await update.message.reply_text("Вы несовершеннолетний? (да/нет)")
        context.user_data['state'] = 'add_credit_history_underage'

    elif user_state == 'add_credit_history_underage':
        response = text.lower()
        if response in ["да", "yes"]:
            context.user_data['is_underage'] = True
        elif response in ["нет", "no"]:
            context.user_data['is_underage'] = False
        else:
            await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет':")
            return

        # Создание записи кредитной истории
        credit_history_create = CreditHistoryCreate(
            organization=context.user_data['organization'],
            has_credit=context.user_data['has_credit'],
            has_criminal_record=context.user_data['has_criminal_record'],
            is_underage=context.user_data['is_underage']
        )

        with get_db() as db:
            credit_history = create_credit_history(db, credit_history_create, user.id)
            await update.message.reply_text(
                f"Кредитная история для {credit_history.organization} добавлена.",
                reply_markup=start_markup
            )
        context.user_data.clear()

    elif text == "Зарегистрироваться":
        await register(update, context)

    elif text == "Войти":
        await login(update, context)

    elif user_state in ['awaiting_amount', 'confirming']:
        # Существующая логика подачи заявки на кредит
        with get_db() as db:
            user = db.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()

            if not user:
                await update.message.reply_text("Вы не зарегистрированы! Используйте /start для регистрации.")
                return

            state = get_user_state(user)

            if not state or not state.current_step:
                await update.message.reply_text("Я не знаю, что вы хотите. Используйте /loan для подачи заявки на кредит.")
                return

            if state.current_step == "awaiting_amount":
                try:
                    amount = float(text)
                    if amount <= 0:
                        raise ValueError
                except ValueError:
                    await update.message.reply_text("Пожалуйста, введите корректную положительную сумму кредита:")
                    return

                # Обновление состояния с введённой суммой
                state.data['amount'] = amount
                state.current_step = "confirming"
                update_user_state(db, user.id, state)

                await update.message.reply_text(f"Вы хотите подать заявку на кредит сумму {amount}. Подтвердите? (да/нет)")

            elif state.current_step == "confirming":
                response = text.lower()
                if response in ["да", "yes", "подтвердить"]:
                    amount = state.data.get('amount')
                    if validate_loan_request(user):
                        loan_request_create = LoginRequestCreate(user_id=user.id, amount=amount)
                        create_login_request(db, loan_request_create)
                        await update.message.reply_text(f"Ваша заявка на кредит сумму {amount} одобрена!")
                    else:
                        await update.message.reply_text("Кредит отклонён по условиям.")
                    # Очистка состояния
                    update_user_state(db, user.id, UserState())
                elif response in ["нет", "no", "отмена"]:
                    await update.message.reply_text("Процесс подачи заявки отменён.")
                    # Очистка состояния
                    update_user_state(db, user.id, UserState())
                else:
                    await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет' для подтверждения заявки.")
            else:
                await update.message.reply_text("Неизвестное состояние. Попробуйте снова.")

    else:
        await update.message.reply_text(
            "Неизвестная команда. Пожалуйста, используйте /start для начала."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /help: Справка по командам.
    """
    help_text = (
        "Вот доступные команды:\n"
        "/start - начать работу с ботом\n"
        "Выберите действие: Зарегистрироваться или Войти\n"
        "/loan - подать заявку на кредит\n"
        "/add_credit_history - добавить кредитную историю\n"
        "/help - показать справку"
    )
    await update.message.reply_text(help_text)

def main():
    """
    Основная функция для запуска бота.
    """
    # Инициализация базы данных
    initialize_database()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("add_credit_history", add_credit_history_command))

    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
