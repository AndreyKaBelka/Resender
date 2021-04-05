from vk_api.bot_longpoll import VkBotMessageEvent


class Message:
    def __init__(self, from_id, text, from_title=None, chat_title=None):
        self._from_id = from_id
        self.chat_title = chat_title
        self.from_title = from_title
        self.text = text
        self._translate = {
            'chat_title': 'Название беседы',
            'from_title': 'От кого',
            'text': 'Текст'
        }

    @staticmethod
    def from_vk(vk_event: VkBotMessageEvent):
        peer_id = vk_event.message.get('peer_id')
        text = vk_event.message.get('text')
        from_title = vk_event.client_info.get('from_title')
        chat_title = vk_event.message.get('chat_title')
        return Message(peer_id, text, from_title, chat_title)

    @staticmethod
    def from_tg(tg_message, user_name):
        text = tg_message.text
        from_title = user_name
        return Message(None, text, from_title)

    def __str__(self):
        res = ''
        for key, val in self.__dict__.items():
            if val is not None and not key.startswith('_'):
                res += f'{self._translate.get(key)} : {val}\n'
        return res

    @property
    def from_id(self):
        return self._from_id
