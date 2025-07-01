import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Настройки Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("telegram-checker-456310-8f0083357ddb.json", scope)
gclient = gspread.authorize(creds)

# 📗 Открываем нужный лист
sheet = gclient.open_by_key("1swCHEEm5u38bJZJMQQj0b6kxWSrjIta_r2nlsEoGibM").sheet1

# 🔄 Храним состояние пользователя
user_states = {}

# 🛠 Логирование (для отладки)
logging.basicConfig(level=logging.INFO)

# Функция старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("▶️ Получена команда /start")
    await update.message.reply_text("Привет! Введи, пожалуйста, свою почту, чтобы мы проверили твой прогресс.")
    user_states[update.effective_chat.id] = "waiting_for_email"

# Функция обработки текстов
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📨 Получено сообщение:", update.message.text)
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id)

    if state == "waiting_for_email":
        email = update.message.text.strip().lower()
        data = sheet.get_all_records()

        student = next((row for row in data if row.get('Email', '').strip().lower() == email), None)

        if student:
            try:
                progress = float(student.get('Progress', 0))
                if progress >= 70:
                    await update.message.reply_text("🎉 У тебя отличный прогресс! Ты можешь участвовать в конкурсе!")
                else:
                    await update.message.reply_text("⏳ Пока ты не проходишь по условиям, но обязательно ждем тебя в следующем конкурсе!")
            except ValueError:
                await update.message.reply_text("😅 Не удалось прочитать процент прогресса. Проверь, всё ли указано верно в таблице.")
        else:
            await update.message.reply_text("😕 Мы не нашли такую почту в базе. Попробуй ещё раз или проверь написание.")
    else:
        await update.message.reply_text("Напиши /start, чтобы начать проверку.")

# 🚀 Запуск бота
if __name__ == "__main__":
    # Вставь сюда свой токен от BotFather
    TOKEN = "7502544999:AAE0upW1g8sQX6xstmMjpOgPgzz3q3-FY5I"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен и ждёт сообщений...")
    print("✅ Попытка запуска polling...")
app.run_polling(close_loop=False)

