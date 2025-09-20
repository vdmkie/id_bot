import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === Получаем токен из переменной окружения ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN не найден. Добавь его в Render → Environment → Environment Variables.")

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для получения ID.\n"
        "Напиши что-нибудь в супергруппе или в топике, и я пришлю ID."
    )

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

    # Если сообщение в топике — покажем его ID
    if msg.message_thread_id:
        reply_text += f"\n🧵 Topic ID: {msg.message_thread_id}"

    await msg.reply_text(reply_text)

# === Запуск приложения ===
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
