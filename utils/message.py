from vk_api.bot_longpoll import VkBotMessageEvent


class Message:
    def __init__(self):
        self.from_id = 0
        self.chat_title = ''
        self.text = ''
        self.from_title = ''

    def from_vk(self, vk_event: VkBotMessageEvent):
        pass

    def from_tg(self, tg_message):
        pass
