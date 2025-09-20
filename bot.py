import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message

    print("==========")
    print(f"Chat title: {chat.title}")
    print(f"Chat ID: {chat.id}")
    print(f"User: {msg.from_user.full_name} ({msg.from_user.id})")
    print(f"Message: {msg.text}")

    if msg.message_thread_id:
        print(f"Topic (message_thread_id): {msg.message_thread_id}")

async def main():
    if not TOKEN:
        raise RuntimeError("❌ TELEGRAM_TOKEN не найден!")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("✅ Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
