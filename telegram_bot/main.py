import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
import dict
from utils.utils import *
from db_module import db_persistence as db

load_dotenv()
key = os.getenv('BOT_TELEGRAM_KEY')
bot = telebot.TeleBot(key)


@bot.message_handler(commands=['start'])
def start(message):
    def get_markup():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Register new account", callback_data='new_acc')) \
            .add(InlineKeyboardButton("Add existence account", callback_data='ex_acc'))
        return markup

    bot.send_message(message.chat.id, dict.START_MESSAGE, reply_markup=get_markup())


@bot.callback_query_handler(func=lambda call: True)
def callback_func(call):
    if call.data == 'new_acc':
        _uuid = get_uuid()
        bot.edit_message_text(text=dict.NEW_ACC_MESSAGE.format(id=_uuid), chat_id=call.message.chat.id,
                              message_id=call.message.id)
        db.insert_new_connection(_uuid=_uuid, tg_id=call.message.chat.id)
    elif call.data == 'ex_acc':
        markup = ForceReply(selective=False)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, dict.EX_ACC_MESSAGE, reply_markup=markup)

        def next_handler_step(message):
            try:
                __uuid = str(uuid.UUID(message.text))
                if db.is_exist(_uuid=__uuid):
                    if not db.get_ids(_uuid=__uuid)[0][2]:
                        db.update_connection({'uuid': __uuid}, {'tgID': message.chat.id})
                        bot.send_message(message.chat.id, "Your account is full registered")
                    else:
                        bot.send_message(message.chat.id, "This account is already registered!")
                else:
                    bot.send_message(message.chat.id, 'Wrong id! Try again...')
            except ValueError:
                bot.send_message(message.chat.id, 'Wrong id! Try again...')

        bot.register_next_step_handler(call.message, next_handler_step)


@bot.message_handler(content_types=['text'])
def reply(message):
    bot.send_message(message.chat.id, "HI")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=5)
