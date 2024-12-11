import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from db import get_db, init_db
from tools import (
    create_user,
    add_credit_history,
    get_user_credit_history,
    delete_user_account,
    update_user_password,
    user_exists
)
from prompts import *  
from shemas import UserCreate, CreditHistoryCreate

init_db()


BOT_TOKEN = "8072664742:AAG257f9Dxsz4yG2VdOoPi8UFtCTZEYfJWg"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
 
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(GREATING)
    context.user_data['state'] = 'ask_account_existence'
    
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(STORY_CLEARED_MSG)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    state = context.user_data.get('state', "ask_account_existence")

    if state == 'ask_account_existence':
        if text in ["да", "yes"]:
            context.user_data['state'] = 'login'
            await update.message.reply_text(CHECK_NAME_PASSWORD)
        elif text in ["нет", "no"]:
            context.user_data['state'] = 'register'
            await update.message.reply_text(CREATE_ACCOUNT)
        else:
            await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет'.")

    elif state == 'register':
        try:
            name, email, phone_number, password = text.split(",")
            with get_db() as db:
                user_create = UserCreate(
                    name=name.strip(),
                    email=email.strip(),
                    phone_number=phone_number.strip(),
                    password=password.strip()
                )
                create_user(db, user_create)
                context.user_data.clear()
                await update.message.reply_text("Регистрация успешна!")
                context.user_data['state'] = 'add_credit_history'
                await update.message.reply_text(ADD_CREDIT_ORGANIZATION_MSG)
        except Exception as e:
            logger.error(f"Ошибка регистрации: {e}")
            await update.message.reply_text(ERROR_REGISTRATION_MSG)

    elif state == 'login':
        try:
            email, password = text.split(",")
            with get_db() as db:
                if user_exists(db, email):
                    context.user_data.clear()
                    await update.message.reply_text("Добро пожаловать! Что будем делать дальше?")
                    context.user_data['state'] = 'add_credit_history'
                    await update.message.reply_text(ADD_CREDIT_ORGANIZATION_MSG)
                else:
                    await update.message.reply_text(ERROR_LOGIN_MSG)
        except Exception as e:
            logger.error(f"Ошибка входа: {e}")
            await update.message.reply_text(ERROR_LOGIN_MSG)

    elif state == 'add_credit_history':
        try:
            data = text.split(",")
            organization, has_credit, has_criminal_record, is_underage, employment_status, monthly_income, monthly_expenses, loan_purpose = map(str.strip, data)

            has_credit = has_credit.lower() in ["да", "yes"]
            has_criminal_record = has_criminal_record.lower() in ["да", "yes"]
            is_underage = is_underage.lower() in ["да", "yes"]
            monthly_income = float(monthly_income)
            monthly_expenses = float(monthly_expenses)

            if monthly_income > 50000 and not has_credit:
                credit_score = 10.0
            elif monthly_income > 50000 or not has_credit:
                credit_score = 5.0
            else:
                credit_score = 2.5

            debt_to_income_ratio = monthly_expenses / monthly_income if monthly_income > 0 else None

            credit_history_create = CreditHistoryCreate(
                organization=organization,
                has_credit=has_credit,
                has_criminal_record=has_criminal_record,
                is_underage=is_underage,
                employment_status=employment_status,
                monthly_expenses=monthly_expenses,
                debt_to_income_ratio=debt_to_income_ratio,
                loan_purpose=loan_purpose,
                credit_score=credit_score
            )
            with get_db() as db:
                user_id = 1
                add_credit_history(db, user_id, credit_history_create)
                context.user_data.clear()
                await update.message.reply_text("Кредитная история добавлена успешно!")
                context.user_data['state'] = 'explain_smart_contracts'
                await update.message.reply_text(EXPLAIN_SMART_CONTRACTS_MSG)
                await update.message.reply_text(OFFER_MICROLOAN_MSG)
        except Exception as e:
            logger.error(f"Ошибка добавления кредитной истории: {e}")
            await update.message.reply_text("Ошибка при добавлении кредитной истории.")

    elif state == 'explain_smart_contracts':
        if text in ["да", "yes"]:
            await update.message.reply_text("Отлично! Мы начнём процесс оформления.")
            context.user_data.clear()
        elif text in ["нет", "no"]:
            await update.message.reply_text("Хорошо, если понадоблюсь, просто напишите.")
            context.user_data.clear()
        else:
            await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет'.")

    elif text == "удалить аккаунт":
        context.user_data['state'] = 'delete_account'
        await update.message.reply_text(DELETE_ACCOUNT_PROMPT)

    elif state == 'delete_account':
        if text == "удалить":
            with get_db() as db:
                email = context.user_data.get('email')  # Предположим, email сохранён в user_data
                delete_user_account(db, email)
                await update.message.reply_text(DELETE_ACCOUNT_SUCCESS)
                context.user_data.clear()
        else:
            await update.message.reply_text(DELETE_ACCOUNT_CANCELLED)
            context.user_data.clear()

    elif text == "сменить пароль":
        context.user_data['state'] = 'change_password'
        await update.message.reply_text(CHANGE_PASSWORD_PROMPT)

    elif state == 'change_password':
        try:
            current_password, new_password = text.split(",")
            with get_db() as db:
                email = context.user_data.get('email')
                if update_user_password(db, email, current_password.strip(), new_password.strip()):
                    await update.message.reply_text(CHANGE_PASSWORD_SUCCESS)
                else:
                    await update.message.reply_text(CHANGE_PASSWORD_FAILED)
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Ошибка смены пароля: {e}")
            await update.message.reply_text(CHANGE_PASSWORD_FAILED)

    else:
        await update.message.reply_text(ANOTHER_THEME[0])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вот доступные команды:\n/start - начать работу\n/clear - очистить сессию"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
