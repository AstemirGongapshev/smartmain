import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)

from db import get_db, init_db
from tools import (
    create_user,
    add_credit_history,
    user_exists
)
from prompts import (
    GREATING,
    CHECK_NAME_PASSWORD,
    CREATE_ACCOUNT,
    ADD_CREDIT_ORGANIZATION_MSG, 
    EXPLAIN_SMART_CONTRACTS_MSG,
    OFFER_MICROLOAN_MSG,
    STORY_CLEARED_MSG,
    ERROR_REGISTRATION_MSG,
    ERROR_LOGIN_MSG,
    ANOTHER_THEME
)

# Инициализация БД
init_db()

# Настройка логирования в отдельный файл process.log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='process.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8072664742:AAG257f9Dxsz4yG2VdOoPi8UFtCTZEYfJWg"


class BotScenario:
    def __init__(self):
        self.logger = logger

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("Войти", callback_data="login_flow")],
            [InlineKeyboardButton("Зарегистрироваться", callback_data="register_flow")]
        ]
        await update.message.reply_text(
            text=GREATING,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Доступные команды:\n/start - начать работу\n/clear - очистить сессию"
        )

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        await update.message.reply_text(STORY_CLEARED_MSG)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "login_flow":
            context.user_data['state'] = 'await_login_input'
            await query.edit_message_text("Введите данные для входа в формате: Имя,Пароль")

        elif data == "register_flow":
            context.user_data['state'] = 'await_register_input'
            await query.edit_message_text("Введите данные для регистрации в формате: Имя,Email,+7XXX...,Пароль")

        elif data == "menu_credit_data":
            context.user_data['state'] = 'await_credit_data'
            await query.edit_message_text(ADD_CREDIT_ORGANIZATION_MSG)

        elif data == "menu_microloan":
            await query.edit_message_text(OFFER_MICROLOAN_MSG)
        elif data == "menu_explain_smart":
            await query.edit_message_text(EXPLAIN_SMART_CONTRACTS_MSG)

        else:
            await query.edit_message_text("Неизвестный выбор.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        state = context.user_data.get('state')

      
        if state == 'await_login_input':
            try:
                name, password = text.split(",")
                name = name.strip()
                password = password.strip()
                with get_db() as db:
                   
                    if user_exists(db, name):
                        await update.message.reply_text("Успешно вошли!")
                        context.user_data.clear()
                  
                        await self.show_post_login_menu(update, context)
                    else:
                        await update.message.reply_text(ERROR_LOGIN_MSG)
                        context.user_data.clear()
            except Exception as e:
                self.logger.error(f"Ошибка входа: {e}")
                await update.message.reply_text(ERROR_LOGIN_MSG)
                context.user_data.clear()

        elif state == 'await_register_input':
          
            try:
                name, email, phone_number, password = text.split(",")
                name = name.strip()
                email = email.strip()
                phone_number = phone_number.strip()
                password = password.strip()

             
                if not phone_number.startswith("+7"):
                    await update.message.reply_text("Номер телефона должен начинаться с +7")
                    return

                with get_db() as db:
                    create_user(db, {
                        "name": name,
                        "email": email,
                        "phone_number": phone_number,
                        "password": password
                    })
                await update.message.reply_text("Успешная регистрация!")
                context.user_data.clear()
                
                await self.show_post_login_menu(update, context)
            except Exception as e:
                self.logger.error(f"Ошибка регистрации: {e}")
                await update.message.reply_text(ERROR_REGISTRATION_MSG)
                context.user_data.clear()

        elif state == 'await_credit_data':

            try:
                data = text.split(",")
                if len(data) < 8:
                    await update.message.reply_text("Пожалуйста, введите все данные через запятую.")
                    return
                (organization, has_credit, has_criminal_record, is_underage,
                 employment_status, monthly_income, monthly_expenses, loan_purpose) = map(str.strip, data)

                has_credit_bool = has_credit.lower() in ["да", "yes"]
                has_criminal_record_bool = has_criminal_record.lower() in ["да", "yes"]
                is_underage_bool = is_underage.lower() in ["да", "yes"]
                monthly_income_val = float(monthly_income)
                monthly_expenses_val = float(monthly_expenses)

                if monthly_income_val > 50000 and not has_credit_bool:
                    credit_score = 10.0
                elif monthly_income_val > 50000 or not has_credit_bool:
                    credit_score = 5.0
                else:
                    credit_score = 2.5

                debt_to_income_ratio = (monthly_expenses_val / monthly_income_val) if monthly_income_val > 0 else None

                credit_history_data = {
                    "organization": organization,
                    "has_credit": has_credit_bool,
                    "has_criminal_record": has_criminal_record_bool,
                    "is_underage": is_underage_bool,
                    "employment_status": employment_status,
                    "monthly_expenses": monthly_expenses_val,
                    "debt_to_income_ratio": debt_to_income_ratio,
                    "loan_purpose": loan_purpose,
                    "credit_score": credit_score
                }

                with get_db() as db:
                    user_id = 1  
                    add_credit_history(db, user_id, credit_history_data)

                await update.message.reply_text("Кредитная история добавлена успешно!")
                context.user_data.clear()
                # Выводим меню снова
                await self.show_post_login_menu(update, context)
            except Exception as e:
                self.logger.error(f"Ошибка добавления кредитной истории: {e}")
                await update.message.reply_text("Ошибка при добавлении кредитной истории.")
                context.user_data.clear()

        else:
          
            await update.message.reply_text(ANOTHER_THEME[0])

    async def show_post_login_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        keyboard = [
            [InlineKeyboardButton("Добавить данные для кредитного рейтинга", callback_data="menu_credit_data")],
            [InlineKeyboardButton("Оформить микрокредит (данные уже в базе)", callback_data="menu_microloan")],
            [InlineKeyboardButton("Что такое смарт-контракт?", callback_data="menu_explain_smart")]
        ]
        await update.message.reply_text(
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


def main():
    scenario = BotScenario()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", scenario.start_command))
    app.add_handler(CommandHandler("clear", scenario.clear_command))
    app.add_handler(CommandHandler("help", scenario.help_command))
    app.add_handler(CallbackQueryHandler(scenario.button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scenario.handle_message))

    logger.info("Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
