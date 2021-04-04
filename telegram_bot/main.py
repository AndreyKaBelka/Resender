import os
from dotenv import load_dotenv
import telebot

load_dotenv()
key = os.getenv('BOT_TELEGRAM_KEY')
bot = telebot.TeleBot(key)


@bot.message_handler(content_types=['text'])
def reply(message):
    print(message)
    bot.send_message(message.chat.id, "HI")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=5)
