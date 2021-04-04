from vk_api.bot_longpoll import VkBotMessageEvent


class Message:
    def __init__(self, from_id, text, from_title=None, chat_title=None):
        self.from_id = from_id
        self.chat_title = chat_title
        self.text = text
        self.from_title = from_title

    @staticmethod
    def from_vk(vk_event: VkBotMessageEvent):
        peer_id = vk_event.message.get('peer_id')
        text = vk_event.message.get('text')
        return Message(peer_id, text)

    @staticmethod
    def from_tg(tg_message):
        peer_id = tg_message.chat.id
        text = tg_message.chat.message
        return Message(peer_id, text)

    def __str__(self):
        return f'{{from_id = {self.from_id}, chat_title = {self.chat_title}, text = {self.text}, from_title = {self.chat_title}}}'
