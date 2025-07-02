import logging
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 📄 Чтение таблицы
CSV_FILE = "students.csv"
df = pd.read_csv(CSV_FILE)

# 🔄 Состояния
user_states = {}

# ▶️ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи, пожалуйста, свою почту — мы проверим твой прогресс.")
    user_states[update.effective_chat.id] = "waiting_for_email"

# 📩 Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id)

    if state == "waiting_for_email":
        email = update.message.text.strip().lower()
        student = df[df["Email"].str.lower().str.strip() == email]

        if not student.empty:
            try:
                progress = float(student["Progress"].values[0])
                if progress >= 70:
                    await update.message.reply_text("🎉 Отличный прогресс! Ты можешь участвовать в конкурсе!")
                else:
                    await update.message.reply_text("⏳ Пока ты не проходишь по условиям, но обязательно ждем тебя в следующем конкурсе!")
            except ValueError:
                await update.message.reply_text("😅 Не получилось прочитать процент прогресса. Проверь таблицу.")
        else:
            await update.message.reply_text("😕 Мы не нашли такую почту в базе.")
    else:
        await update.message.reply_text("Напиши /start, чтобы начать.")

# 🚀 Запуск
if __name__ == "__main__":
    import os

    TOKEN = os.getenv("BOT_TOKEN")

    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен")
    app.run_polling(close_loop=False)
