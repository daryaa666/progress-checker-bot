import logging
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

# 📦 Загрузка CSV
df = pd.read_csv("students.csv")

# 📍 Храним состояния
user_states = {}

# 🛠 Логирование
logging.basicConfig(level=logging.INFO)

# ▶️ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи, пожалуйста, свою почту, чтобы мы проверили твой прогресс.")
    user_states[update.effective_chat.id] = "waiting_for_email"

# 💬 Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id)

    if state == "waiting_for_email":
        email = update.message.text.strip().lower()
        student = df[df["Email"].str.lower() == email]

        if not student.empty:
            progress = float(student["Progress"].values[0])
            if progress >= 70:
                await update.message.reply_text("🎉 У тебя отличный прогресс! Ты можешь участвовать в конкурсе!")
            else:
                await update.message.reply_text("⏳ Пока ты не проходишь по условиям, но обязательно ждем тебя в следующем конкурсе!")
        else:
            await update.message.reply_text("😕 Мы не нашли такую почту в базе. Проверь написание и попробуй снова.")
    else:
        await update.message.reply_text("Напиши /start, чтобы начать проверку.")

# 🚀 Запуск
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен и ждёт сообщений...")
    app.run_polling(close_loop=False)
