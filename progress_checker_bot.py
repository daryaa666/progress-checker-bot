import logging
import os
import csv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 📦 Настройки логирования
logging.basicConfig(level=logging.INFO)

# 🗂 Загрузка CSV базы
def load_data():
    data = []
    with open("progress.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# 🔄 Состояние пользователей
user_states = {}

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
        students = load_data()
        student = next((s for s in students if s.get('Email', '').strip().lower() == email), None)

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

# 🚀 Запуск
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")

    if not TOKEN:
        raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен и ждёт сообщений...")
    app.run_polling()
