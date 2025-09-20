from telegram.ext import Updater, MessageHandler, Filters

# === Вставь сюда токен своего бота ===
TOKEN = 8083231919:AAHtt6c7wE1d-V3f2eBO3WDjXJ7AxSxEzYs

def message_handler(update, context):
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

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.all, message_handler))

    print("Бот запущен. Напиши что-нибудь в группу/топик.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
