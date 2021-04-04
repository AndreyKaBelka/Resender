import asyncio
import os

from aiovk import TokenSession, API
from dotenv import load_dotenv
from aiovk.longpoll import BotsLongPoll
from vk_api.bot_longpoll import VkBotEventType, VkBotMessageEvent, VkBotEvent
from vk_bot.bot import VkBot

load_dotenv()


def main():
    loop = asyncio.get_event_loop()
    ses = TokenSession(access_token=str(os.getenv('BOT_VK_KEY')))
    api = API(ses)
    lp = BotsLongPoll(api, int(os.getenv('GROUP_ID')), version=100)

    async def write_msg(vk_bot: VkBot):
        await api.messages.send(peer_id=int(vk_bot.peer_id), message=vk_bot.text, keyboard=vk_bot.keyboard)

    async def edit_last_message(vk_bot: VkBot):
        await api.messages.edit(peer_id=int(vk_bot.peer_id), message=vk_bot.text,
                                conversation_message_id=vk_bot.conversation_message_id)

    async def main_loop():
        async for event in lp.iter():
            event = VkBotEvent(event)
            if event.type == VkBotEventType.MESSAGE_NEW:
                event = VkBotMessageEvent(event.raw)
                vk_bot = VkBot(event)
                vk_bot.new_message()
                await write_msg(vk_bot)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                event = VkBotMessageEvent(event.raw)
                vk_bot = VkBot(event)
                vk_bot.new_callback_answer()
                await edit_last_message(vk_bot)

    loop.run_until_complete(main_loop())


if __name__ == '__main__':
    main()
