import asyncio

from vk_bot import *
from vk_api.bot_longpoll import VkBotEventType, VkBotMessageEvent, VkBotEvent
from vk_bot.bot import VkBot


def main():
    loop = asyncio.get_event_loop()

    async def edit_last_message(vk_bot: VkBot):
        await api.messages.edit(peer_id=int(vk_bot.peer_id), message=vk_bot.text,
                                conversation_message_id=vk_bot.conversation_message_id)

    async def get_user_title(vk_bot: VkBot):
        return await api.users.get(user_ids=int(vk_bot.from_id))

    async def get_chat_title(vk_bot: VkBot):
        convs = await api.messages.getConversationsById(peer_ids=vk_bot.peer_id)
        for conv in convs['items']:
            if conv['peer']['type'] == 'chat' and conv['peer']['id'] == vk_bot.peer_id:
                return conv['chat_settings']['title']

    async def main_loop():
        async for event in lp.iter():
            event = VkBotEvent(event)
            if event.type == VkBotEventType.MESSAGE_NEW:
                event = VkBotMessageEvent(event.raw)
                vk_bot = VkBot(event)
                vk_bot.from_user = (await get_user_title(vk_bot))[0]
                vk_bot.chat_title = await get_chat_title(vk_bot)
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
