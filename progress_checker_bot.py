import logging
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 📥 Загружаем CSV-файл с прогрессом
df = pd.read_csv("students.csv")

# 🔄 Храним состояние пользователей
user_states = {}

# 🛠 Логирование
logging.basicConfig(level=logging.INFO)

# ▶️ Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи, пожалуйста, свою почту, чтобы мы проверили твой прогресс.")
    user_states[update.effective_chat.id] = "waiting_for_email"

# 📨 Обработка текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id)

    if state == "waiting_for_email":
        email = update.message.text.strip().lower()
        student_row = df[df["Email"].str.lower() == email]

        if not student_row.empty:
            try:
                progress_str = str(student_row["Progress"].values[0]).replace("%", "").strip()
                progress = float(progress_str)
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
    import os
    TOKEN = os.getenv("BOT_TOKEN")  # токен из переменной окружения

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен и ждёт сообщений...")
    app.run_polling()
