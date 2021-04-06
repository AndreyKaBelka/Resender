import telegram_bot
import vk_bot
from utils.message import Message


def from_vk_to_tg(tg_id, message: Message):
    def get_keyboard_to_reply():
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("Reply to chat", callback_data=f'reply_to:{message.from_id}'))
        return markup

    telegram_bot.bot.send_message(tg_id, message, reply_markup=get_keyboard_to_reply())


def from_tg_to_vk(vk_id, message: Message):
    vk_bot.loop.run_until_complete(vk_bot.write_msg(message=message, peer_id=vk_id))
