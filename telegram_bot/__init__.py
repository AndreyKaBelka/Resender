import os
from dotenv import load_dotenv
import telebot

load_dotenv()
key = os.getenv('BOT_TELEGRAM_KEY')
bot = telebot.TeleBot(key)


def listener(messages):
    print('Got new message!')


bot.set_update_listener(listener)
