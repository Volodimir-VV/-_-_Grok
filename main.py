import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

# 🔐 Токени з .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 🤖 Історія повідомлень для памʼяті (у памʼяті бота)
user_histories = {}

# 🪵 Логування
logging.basicConfig(level=logging.INFO)

# 🌐 Запит до Groq API
def chat_with_groq(user_id, message):
    history = user_histories.get(user_id, [])
    history.append({"role": "user", "content": message})

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": history,
            "temperature": 0.7
        }
    )

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        history.append({"role": "assistant", "content": reply})
        user_histories[user_id] = history[-10:]  # зберігаємо тільки останні 10
        return reply
    else:
        logging.error("Groq error: %s", response.text)
        return "⚠️ Виникла помилка при зверненні до ШІ 😢"

# 📩 Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    await update.message.chat.send_action(action="typing")
    reply = chat_with_groq(user_id, user_message)

    await update.message.reply_text(reply)

# 🚀 Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("✅ Бот запущено!")
    app.run_polling()
