import logging
from telegram import Update, ReplyKeyboardMarkup
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
    create_credit_history,
    authenticate_user
)
from shemas import  CreditHistoryCreate, UserCreate
from models import User

BOT_TOKEN = "8072664742:AAG257f9Dxsz4yG2VdOoPi8UFtCTZEYfJWg"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


init_db()

start_keyboard = [['Зарегистрироваться', 'Войти'], ['Добавить кредитную историю']]
start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True, resize_keyboard=True)

REGISTER_NAME = "register_name"
REGISTER_PASSWORD = "register_password"
LOGIN_ID = "login_id"
LOGIN_PASSWORD = "login_password"
ADD_CREDIT_ORGANIZATION = "add_credit_organization"
ADD_CREDIT_HAS_CREDIT = "add_credit_has_credit"
ADD_CREDIT_HAS_CRIMINAL = "add_credit_has_criminal"
ADD_CREDIT_UNDERAGE = "add_credit_underage"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Добро пожаловать! Я первый чат-бот со встроенным смарт-контрактом. \n"
        "Я могу помочь вам зарегистрироваться, войти или добавить кредитную историю. \n"
        "Выберите действие:",
        reply_markup=start_markup
    )

def handle_user_state(state, update, context):
    text = update.message.text.strip()

    if state == REGISTER_NAME:
        context.user_data['name'] = text
        context.user_data['state'] = REGISTER_PASSWORD
        return "Введите пароль:"

    elif state == REGISTER_PASSWORD:
        name = context.user_data['name']
        password = text

        with get_db() as db:
            existing_user = db.query(User).filter_by(name=name).first()
            if existing_user:
                return f"Имя {name} уже занято. Попробуйте другое."
            try:
                user_create = UserCreate(name=name, password=password)
                user = create_user(db, user_create)
                context.user_data.clear()
                return f"Поздравляем, {user.name}! Вы успешно зарегистрированы."
            except Exception as e:
                logger.error(f"Ошибка при регистрации пользователя: {e}")
                return "Произошла ошибка при регистрации. Попробуйте снова."

    elif state == LOGIN_ID:
        context.user_data['login_id'] = text
        context.user_data['state'] = LOGIN_PASSWORD
        return "Введите пароль:"

    elif state == LOGIN_PASSWORD:
        login_id = context.user_data['login_id']
        password = text
        with get_db() as db:
            user = authenticate_user(db, login_id, password)
            if user:
                context.user_data.clear()
                return f"Добро пожаловать, {user.name}!"
            else:
                return "Неверные учетные данные. Попробуйте снова."

    elif state == ADD_CREDIT_ORGANIZATION:
        context.user_data['organization'] = text
        context.user_data['state'] = ADD_CREDIT_HAS_CREDIT
        return "Есть ли у вас кредиты в этой организации? (да/нет)"

    elif state == ADD_CREDIT_HAS_CREDIT:
        context.user_data['has_credit'] = text.lower() in ["да", "yes"]
        context.user_data['state'] = ADD_CREDIT_HAS_CRIMINAL
        return "Есть ли у вас судимости? (да/нет)"

    elif state == ADD_CREDIT_HAS_CRIMINAL:
        context.user_data['has_criminal_record'] = text.lower() in ["да", "yes"]
        context.user_data['state'] = ADD_CREDIT_UNDERAGE
        return "Вы несовершеннолетний? (да/нет)"

    elif state == ADD_CREDIT_UNDERAGE:
        context.user_data['is_underage'] = text.lower() in ["да", "yes"]
        organization = context.user_data['organization']
        has_credit = context.user_data['has_credit']
        has_criminal_record = context.user_data['has_criminal_record']
        is_underage = context.user_data['is_underage']

        credit_history_create = CreditHistoryCreate(
            organization=organization,
            has_credit=has_credit,
            has_criminal_record=has_criminal_record,
            is_underage=is_underage
        )

        with get_db() as db:
            user_id = 1  
            create_credit_history(db, credit_history_create, user_id)
            context.user_data.clear()
            return f"Кредитная история для {organization} добавлена."

    else:
        return "Что то пошло не так. Попробуйте снова."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip().lower()
    user_state = context.user_data.get('state', None)

    if text in ["привет", "здравствуйте"]:
        await update.message.reply_text(
            "Привет! Я первый чат-бот со встроенным смарт-контрактом. Чем могу помочь?"
        )
        return

    if text in ["зарегистрироваться", "войти", "добавить кредитную историю"]:
        if text == "зарегистрироваться":
            context.user_data['state'] = REGISTER_NAME
            await update.message.reply_text("Начинаем регистрацию. Пожалуйста скажите как вас зовут:")
        elif text == "войти":
            context.user_data['state'] = LOGIN_ID
            await update.message.reply_text("Вход. Введите ваш ID:")
        elif text == "добавить кредитную историю":
            context.user_data['state'] = ADD_CREDIT_ORGANIZATION
            await update.message.reply_text("Введите название организации:")
        return

    if user_state:
        response = handle_user_state(user_state, update, context)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Упс!. Я такого не знаю давайте вернемся к делу")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Вот доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать справку"
    )

def main():

    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
