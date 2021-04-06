import asyncio

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
loop = asyncio.get_event_loop()


async def write_msg(vk_bot: VkBot = None, message: Message = None, peer_id=None):
    if vk_bot and vk_bot.text is not None:
        await api.messages.send(peer_id=int(vk_bot.peer_id), message=vk_bot.text, keyboard=vk_bot.keyboard)
    elif message:
        await api.messages.send(peer_id=peer_id, message=message)


async def get_user_title(vk_bot: VkBot):
    res = (await api.users.get(user_ids=int(vk_bot.from_id)))[0]
    return f"{res['first_name']} {res['last_name']}"


async def get_chat_title(vk_bot: VkBot = None, peer_id=None):
    peer_id = vk_bot.peer_id if vk_bot else peer_id
    convs = await api.messages.getConversationsById(peer_ids=peer_id)
    for conv in convs['items']:
        if conv['peer']['type'] == 'chat' and conv['peer']['id'] == peer_id:
            return conv['chat_settings']['title']


async def edit_last_message(vk_bot: VkBot):
    await api.messages.edit(peer_id=int(vk_bot.peer_id), message=vk_bot.text,
                            conversation_message_id=vk_bot.conversation_message_id)
