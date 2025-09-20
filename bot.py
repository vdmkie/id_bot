from telegram.ext import Updater, MessageHandler, Filters

TOKEN = 8498478959:AAGIQJUxkFGaiWXn_PtiSmbvk0-t2nBU_AY

def message_handler(update, context):
    chat = update.effective_chat
    msg = update.message

    print("==========")
    print(f"Chat title: {chat.title}")
    print(f"Chat ID: {chat.id}")
    if msg.message_thread_id:
        print(f"Topic ID (message_thread_id): {msg.message_thread_id}")
    print(f"User: {msg.from_user.full_name} ({msg.from_user.id})")
    print(f"Message: {msg.text}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.all, message_handler))

    print("Бот запущен...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
