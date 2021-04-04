from vk_api.bot_longpoll import VkBotMessageEvent
import re
import vk_api.keyboard as vk_keyboards


class VkBot:
    def __init__(self, event: VkBotMessageEvent):
        self.event = event
        try:
            self.peer_id = event.message.get('peer_id')
        except AttributeError:
            self.peer_id = event.object.get('peer_id')

        try:
            self.conversation_message_id = event.message.get('conversation_message_id')
        except AttributeError:
            self.conversation_message_id = event.object.get('conversation_message_id')

        try:
            self.payload = event.object.get('payload')
        except AttributeError:
            self.payload = {}

        self.message_handlers = dict([
            (r'/start', self.start),
            (r'.', self.message)
        ])

        self.callback = dict([
            ('new_acc', self.new_acc),
            ('ex_acc', self.ex_acc)
        ])
        self.text = None
        self.keyboard = {}

    def registration_keyboard(self):
        keyboard = vk_keyboards.VkKeyboard(inline=True)
        keyboard.add_callback_button('Register new account', payload={'type': 'new_acc'})
        keyboard.add_callback_button('Add existence account', payload={'type': 'ex_acc'})
        return keyboard.get_keyboard()

    def new_message(self):
        if self.event.from_user:
            for key, func in self.message_handlers.items():
                if re.match(key, self.event.message.text):
                    func()
        elif self.event.from_chat:
            pass

    def new_callback_answer(self):
        self.callback.get(self.payload.get('type'))()

    def new_acc(self):
        self.text = 'NEw Acc!'

    def ex_acc(self):
        self.text = 'Ex acc!'

    def start(self):
        self.text = "From user!"
        self.keyboard = self.registration_keyboard()

    def message(self):
        self.text = "Simple message!"

    def get_user_name(self):
        pass
