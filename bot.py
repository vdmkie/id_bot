import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Берём токен из переменной окружения (Render → Environment → TELEGRAM_TOKEN)
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Логирование (попадает в Render Logs)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === Хендлер всех сообщений ===
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message

    # Собираем текст ответа
    reply_text = (
        f"📌 Chat title: {chat.title}\n"
        f"💬 Chat ID: {chat.id}\n"
        f"👤 User: {msg.from_user.full_name} ({msg.from_user.id})\n"
        f"✉️ Message: {msg.text}\n"
    )

    # Если сообщение в топике → добавляем ID топика
    if msg.message_thread_id:
        reply_text += f"🧵 Topic ID: {msg.message_thread_id}"

    # Отвечаем в том же чате / топике
    await msg.reply_text(reply_text)

# === Основная функция ===
async def main():
    if not TOKEN:
        raise RuntimeError("❌ TELEGRAM_TOKEN не найден. Задай его в Render!")

    # Создаём приложение
    app = Application.builder().token(TOKEN).build()

    # Ловим все сообщения (и текст, и медиа, и в топиках)
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("✅ Бот запущен")
    await app.run_polling()

# === Точка входа ===
if __name__ == "__main__":
    asyncio.run(main())
