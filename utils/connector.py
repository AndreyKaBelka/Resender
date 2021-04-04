from utils.message import Message
import vk_bot
import telegram_bot


def from_vk_to_tg(tg_id, message: Message):
    telegram_bot.bot.send_message(tg_id, message)


def from_tg_to_vk(vk_id, message: Message):
    vk_bot.write_msg(message=message, peer_id=vk_id)
