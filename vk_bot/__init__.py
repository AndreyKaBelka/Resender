from aiovk.longpoll import BotsLongPoll
import os
from aiovk import TokenSession, API
from dotenv import load_dotenv
from utils.message import Message

from vk_bot.bot import VkBot

load_dotenv()

ses = TokenSession(access_token=str(os.getenv('BOT_VK_KEY')))
api = API(ses)
lp = BotsLongPoll(api, int(os.getenv('GROUP_ID')), version=100)


async def write_msg(vk_bot: VkBot = None, message: Message = None, peer_id=None):
    if vk_bot and vk_bot.text is not None:
        await api.messages.send(peer_id=int(vk_bot.peer_id), message=vk_bot.text, keyboard=vk_bot.keyboard)
    elif message:
        await api.messages.send(peer_id=peer_id, message=message)
