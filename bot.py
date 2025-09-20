import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === Берём токен из переменной окружения ===
TOKEN = os.getenv("BOT_TOKEN")

# Логирование (для дебага на Render)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message

    print("==========")
    print(f"Chat title: {chat.title}")
    print(f"Chat ID: {chat.id}")   # ID супергруппы
    print(f"User: {msg.from_user.full_name} ({msg.from_user.id})")
    print(f"Message: {msg.text}")

    # Если сообщение в топике (форум)
    if msg.message_thread_id:
        print(f"Topic (message_thread_id): {msg.message_thread_id}")

async def main():
    if not TOKEN:
        raise RuntimeError("Не найден BOT_TOKEN. Установи переменную окружения!")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("Бот запущен. Жду сообщения...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
