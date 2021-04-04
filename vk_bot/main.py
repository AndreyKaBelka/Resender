import asyncio

from vk_bot import *
from vk_api.bot_longpoll import VkBotEventType, VkBotMessageEvent, VkBotEvent
from vk_bot.bot import VkBot


def main():
    loop = asyncio.get_event_loop()

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
