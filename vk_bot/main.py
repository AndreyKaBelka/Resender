from vk_bot import *
from vk_api.bot_longpoll import VkBotEventType, VkBotMessageEvent, VkBotEvent
from vk_bot.bot import VkBot
from vk_bot.dict import HELP_MESSAGE


def main():
    async def main_loop():
        async for event in lp.iter():
            event = VkBotEvent(event)
            if event.type == VkBotEventType.MESSAGE_NEW:
                event = VkBotMessageEvent(event.raw)
                action = event.message.get('action')
                if action is not None and action.get('type') == 'chat_invite_user':
                    vk_bot = VkBot(event)
                    vk_bot.text = HELP_MESSAGE
                    await write_msg(vk_bot)
                else:
                    vk_bot = VkBot(event)
                    vk_bot.from_user = await get_user_title(vk_bot)
                    vk_bot.chat_title = await get_chat_title(vk_bot)
                    vk_bot.new_message()
                    await write_msg(vk_bot)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                event = VkBotMessageEvent(event.raw)
                vk_bot = VkBot(event)
                vk_bot.from_user = await get_user_title(vk_bot)
                vk_bot.new_callback_answer()
                await edit_last_message(vk_bot)

    loop.run_until_complete(main_loop())


if __name__ == '__main__':
    main()
