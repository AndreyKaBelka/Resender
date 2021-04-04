from vk_api.bot_longpoll import VkBotMessageEvent


class Message:
    def __init__(self, from_id, text, from_title=None, chat_title=None):
        self._from_id = from_id
        self.chat_title = chat_title
        self.from_title = from_title
        self.text = text

    @staticmethod
    def from_vk(vk_event: VkBotMessageEvent):
        peer_id = vk_event.message.get('peer_id')
        text = vk_event.message.get('text')
        from_title = vk_event.client_info.get('from_title')
        chat_title = vk_event.message.get('chat_title')
        return Message(peer_id, text, from_title, chat_title)

    @staticmethod
    def from_tg(tg_message):
        peer_id = tg_message.chat.id
        text = tg_message.chat.message
        from_title = tg_message.chat.from_title
        return Message(peer_id, text, from_title)

    def __str__(self):
        res = ''
        for key, val in self.__dict__.items():
            if val is not None and not key.startswith('_'):
                res += f'{key} : {val}\n'
        return res
