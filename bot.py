import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN не найден. Задай переменную окружения в Render!")

# === Хендлер для любых сообщений ===
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
        reply_text += f"🧵 Topic ID: {msg.message_thread_id}"

    await msg.reply_text(reply_text)

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("✅ Бот запущен (Python 3.13)")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
