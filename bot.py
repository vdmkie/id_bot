import os
from telegram.ext import Application, MessageHandler, filters

# Берём токен из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Обработчик сообщений
async def message_handler(update, context):
    chat = update.effective_chat
    msg = update.message

    print("==========")
    print(f"Chat title: {chat.title}")
    print(f"Chat ID: {chat.id}")
    if msg.message_thread_id:
        print(f"Topic ID: {msg.message_thread_id}")
    print(f"User: {msg.from_user.full_name} ({msg.from_user.id})")
    print(f"Message: {msg.text}")

# Точка входа
def main():
    if not TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN не найден. Добавь его в Render → Environment.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
