import logging
import asyncio
import random
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
import time 
from models import UserCreate, CreditHistoryCreate
from DataBase.db import get_db, init_db
from DataBase.tools import (
    create_user,
    add_credit_history,
    user_exists
)
import random
from DataBase.data_models import User, CreditHistory
from DataBase.prompts import (
    GREATING,
    CHECK_NAME_PASSWORD,
    CREATE_ACCOUNT,
    ADD_CREDIT_ORGANIZATION_MSG,
    EXPLAIN_SMART_CONTRACTS_MSG,
    OFFER_MICROLOAN_MSG,
    STORY_CLEARED_MSG,
    ERROR_REGISTRATION_MSG,
    ERROR_LOGIN_MSG,
    ANOTHER_THEME,
    COMPILE,
    DEPLOY
)


init_db()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
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
            await query.edit_message_text(CHECK_NAME_PASSWORD)

        elif data == "register_flow":
           
            context.user_data['state'] = 'await_register_input'
            await query.edit_message_text(CREATE_ACCOUNT)

        elif data == "menu_credit_data":
           
            context.user_data['state'] = 'await_credit_data'
            await query.edit_message_text(ADD_CREDIT_ORGANIZATION_MSG)



        elif data == "menu_microloan":
           
            await query.edit_message_text(OFFER_MICROLOAN_MSG)
            
            for i in range(5, 0, -1):
                await asyncio.sleep(1) 
                await query.edit_message_text(f"Компилируем... {i}")
            
            await asyncio.sleep(1)  
            await query.edit_message_text("Компиляция завершена!")
            for i in range(3, 0, -1):
                await asyncio.sleep(1) 
                await query.edit_message_text(f"Деплоим... {i}")

            await query.edit_message_text("Деплой завершён!")
            await asyncio.sleep(1)  
            await query.message.reply_text("Отлично, смарт-контракт успешно скомпилирован и запущен:")

            SAMPLE = ["contract.png", "contract_2.png", "contract_3.png"]
            rand = random.choice(SAMPLE)
            photo_path = os.path.join("Photo", rand)

            if os.path.exists(photo_path):
                with open(photo_path, "rb") as photo:
                    await query.message.reply_photo(photo=photo)
            else:
                await query.message.reply_text("Фото смарт-контракта не найдено.")

   
            await self.show_post_login_menu(update, context)


        elif data == "menu_explain_smart":
            # video_path = os.path.join("Photo", "my_video.mp3")
            # with open(video_path, "rb") as video:
            #     await query.message.reply_video(video=video, caption="Вот ваше видео!")

            await query.edit_message_text(EXPLAIN_SMART_CONTRACTS_MSG)
            photo_path_info = os.path.join("Photo", "info.jpg")
            with open(photo_path_info, "rb") as photo:
                await query.message.reply_photo(photo=photo)
                context.user_date["state"] = "menu_explain_smart"

        else:
            await query.edit_message_text("Неизвестный выбор.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        state = context.user_data.get('state')

        logging.info(f'This user text:{text}, state: {state}')

        if text == "Привет" and not state:
      
            await update.message.reply_text(GREATING)
            # context.user_data['state'] = 'await_login_input'
            # await update.message.reply_text(CHECK_NAME_PASSWORD)
            return

       
        if state == 'await_login_input':
          
            try:
                name, password = text.split(",")
                name = name.strip()
                password = password.strip()

                with get_db() as db:
                    name_, password_ = user_exists(db, name, password)
                
                if name_ and password_:
                    await update.message.reply_text(f"{name} вы успешно вошли!")
                    
                    context.user_data.clear()
                    await self.show_post_login_menu(update, context)
                else:
                    
                    await update.message.reply_text(ERROR_LOGIN_MSG)
                    await update.message.reply_text("Попробуйте снова: введите имя и пароль через запятую.")
                  
            except Exception as e:
                self.logger.error(f"Ошибка входа: {e}")
                await update.message.reply_text(ERROR_LOGIN_MSG)
                await update.message.reply_text("Попробуйте снова: введите имя и пароль через запятую.")
           

        elif state == 'await_register_input':
       
            try:
                name, email, phone_number, password = text.split(",")
                creds_new_user = dict(
                    name=name.strip(),
                    email=email.strip(),
                    phone_number=phone_number.strip(),
                    password=password.strip()
                )
                new_user = UserCreate(**creds_new_user)

                with get_db() as db:
                    create_user(db, new_user)
                await update.message.reply_text("Успешная регистрация!")
                context.user_data.clear()
                await self.show_post_login_menu(update, context)
            except Exception as e:
                self.logger.error(f"Ошибка регистрации: {e}")
                await update.message.reply_text(ERROR_REGISTRATION_MSG)
                await update.message.reply_text("Попробуйте снова: имя, e-mail, телефон, пароль через запятую.")
                

        elif state == 'await_credit_data':
            
            try:
                data = text.split(",")
                if len(data) < 6:
                    await update.message.reply_text(
                        "Нужно 6 параметров: Имя, есть ли кредит(да/нет), доход, паспортные данные, занятость, цель кредита.\nПопробуйте снова."
                    )
                    return

                name_for_credit, has_credit, income, pasport_data, employment_status, loan_purpose = map(str.strip, data)

                with get_db() as db:
                    name_for_credit_check, _ = user_exists(db, name_for_credit, "None")

                if not name_for_credit_check:
                    await update.message.reply_text("Такой пользователь не существует. Попробуйте снова.")
                    return

                has_credit_bool = has_credit.lower() in ["да", "yes"]
                income_val = int(income)

                credit_info = dict(
                    has_credit=has_credit_bool,
                    income=income_val,
                    pasport_data=pasport_data,
                    employment_status=employment_status,
                    loan_purpose=loan_purpose
                )

                credit_history_data = CreditHistoryCreate(**credit_info)

                with get_db() as db:
                    user_id = db.query(User).filter_by(name=name_for_credit).first().id
                    add_credit_history(db, user_id, credit_history_data)

                await update.message.reply_text("Кредитная история успешно добавлена!")
                context.user_data.clear()
                await self.show_post_login_menu(update, context)
            except ValueError as e:
                self.logger.error(f"Error:{str(e)}")
                await update.message.reply_text("Упс, ошибка обработки данных. Попробуйте снова.")
               
            except Exception as e:
                self.logger.error(f"Ошибка добавления кредитной истории: {str(e)}")
                await update.message.reply_text("Произошла ошибка, попробуйте снова.")

        # elif state == "menu_explain_smart":
        #     await self.show_post_login_menu(update, context)

        else:
           

            await update.message.reply_text(random.choice(ANOTHER_THEME))

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
