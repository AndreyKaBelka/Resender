import telegram_bot
import vk_bot
from utils.message import Message
from db_module import db_persistence


def from_vk_to_tg(tg_id, message: Message):
    def get_keyboard_to_reply():
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("Reply to chat", callback_data=f'reply_to:{message.from_id}'))
        return markup

    telegram_bot.bot.send_message(tg_id, message, reply_markup=get_keyboard_to_reply())


def from_tg_to_vk(vk_id, message: Message):
    vk_bot.loop.run_until_complete(vk_bot.write_msg(message=message, peer_id=vk_id))
    chat_listeners = db_persistence.get_chat_listeners(vk_id)
    message._tg_id = message.from_id
    message._from_id = vk_id
    if len(chat_listeners) > 0:
        message.chat_title = vk_bot.loop.run_until_complete(vk_bot.get_chat_title(peer_id=vk_id))
        for chat_listener in chat_listeners:
            chat_listener_id = int(chat_listener[0])
            if db_persistence.is_exist(vk_id=chat_listener_id) \
                    and db_persistence.is_fully_registered(chat_listener_id):
                tg_id = db_persistence.get_ids(vk_id=chat_listener_id)[0][2]
                if tg_id != message.tg_id:
                    from_vk_to_tg(tg_id, message)
