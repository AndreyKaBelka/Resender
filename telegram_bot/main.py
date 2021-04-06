from telegram_bot import *
from telebot.types import ForceReply
from telegram_bot import dict
from utils import connector
from utils.message import Message
from utils.utils import *
from db_module import db_persistence as db


@bot.message_handler(commands=['start'])
def start(message):
    def get_markup():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Register new account", callback_data='new_acc')) \
            .add(InlineKeyboardButton("Add existence account", callback_data='ex_acc'))
        return markup

    bot.send_message(message.chat.id, dict.START_MESSAGE, reply_markup=get_markup())
    db.insert_or_update_tg_state(message.chat.id)


@bot.message_handler(commands=['chat'])
def chat_choose(message):
    tg_id = message.chat.id
    state = db.get_tg_state(tg_id)
    if state is not None:
        if state == TgUserState.INITIAL:
            chats = db.get_listener_chats_from_tg(tg_id)
            bot.send_message(tg_id, 'Select chat:', reply_markup=get_keyboard_for_chats(chats, 1))
            db.insert_or_update_tg_state(tg_id, TgUserState.CHAT)
        else:
            bot.send_message(message.chat.id, 'Something went wrong! Try again')
            db.insert_or_update_tg_state(message.chat.id, TgUserState.INITIAL)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, dict.HELP_MESSAGE)


def is_int(call):
    try:
        int(call.data)
        return True
    except ValueError:
        return False


@bot.callback_query_handler(func=is_int)
def get_chat_id(call):
    tg_id = call.message.chat.id
    vk_chat_id = int(call.data)

    def nex_handler(message, vk_peer_id):
        user_name = db.get_username_from_tg(message.chat.id)
        vk_msg = Message.from_tg(message, user_name)
        connector.from_tg_to_vk(vk_peer_id, vk_msg)
        db.insert_or_update_tg_state(message.chat.id, TgUserState.INITIAL)

    bot.send_message(tg_id, 'Write message for chat!')
    db.insert_or_update_tg_state(tg_id, TgUserState.MESSAGE)
    bot.register_next_step_handler(call.message, nex_handler, vk_peer_id=vk_chat_id)


@bot.callback_query_handler(func=lambda call: 'bck:' in call.data or 'fwd:' in call.data)
def paginating(call):
    page_num = int(call.data[4:])
    tg_id = call.message.chat.id
    if 'bck:' in call.data:
        bot.edit_message_reply_markup(tg_id, call.message.id,
                                      reply_markup=get_keyboard_for_chats(db.get_listener_chats_from_tg(tg_id),
                                                                          page_num - 1))
    elif 'fwd:' in call.data:
        bot.edit_message_reply_markup(tg_id, call.message.id,
                                      reply_markup=get_keyboard_for_chats(db.get_listener_chats_from_tg(tg_id),
                                                                          page_num + 1))
    else:
        bot.send_message(call.message.chat.id, 'Something went wrong! Try again')
        db.insert_or_update_tg_state(call.message.chat.id, TgUserState.INITIAL)


@bot.callback_query_handler(func=lambda call: True)
def callback_func(call):
    if call.data == 'new_acc':
        if db.is_exist(tg_id=call.message.chat.id):
            bot.send_message(call.message.chat.id, dict.ALREADY_EXIST)
            return
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
    elif 'reply_to' in call.data:
        if db.get_tg_state(call.message.chat.id) == TgUserState.INITIAL:
            vk_peer_id = call.data[9:]
            call.data = vk_peer_id
            get_chat_id(call)
        else:
            bot.send_message(call.message.chat.id, 'Something went wrong! Try again')
            db.insert_or_update_tg_state(call.message.chat.id, TgUserState.INITIAL)


@bot.message_handler(content_types=['text'])
def reply(message):
    bot.send_message(message.chat.id, "I don`t understand you. Type /help to see available commands")


def main():
    return bot.infinity_polling()


if __name__ == '__main__':
    main()
