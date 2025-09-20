import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Берём токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN не найден. Добавь его в Render → Environment → Environment Variables.")

# === Обработка любого сообщения ===
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message

    reply_text = (
        f"📌 Chat title: {chat.title}\n"
        f"💬 Chat ID: {chat.id}\n"
        f"👤 User: {msg.from_user.full_name} ({msg.from_user.id})\n"
        f"✉️ Message: {msg.text}\n"
    )

    if msg.message_thread_id:
        reply_text += f"\n🧵 Topic ID: {msg.message_thread_id}"

    await msg.reply_text(reply_text)

# === Основной запуск ===
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("✅ Бот запущен и работает на Render!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
