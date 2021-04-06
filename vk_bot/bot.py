import re
import uuid

import vk_api.keyboard as vk_keyboards
from vk_api.bot_longpoll import VkBotMessageEvent

from vk_bot import dict as vk_dict
from db_module import db_persistence
from utils import utils, connector
from utils.message import Message


class UserState:
    INITIAL = 0
    ID = 1


class VkBot:
    def __init__(self, event: VkBotMessageEvent):
        self.event = event
        try:
            self.peer_id = event.message['peer_id']
        except TypeError:
            self.peer_id = event.obj['peer_id']

        try:
            self.from_id = event.message['from_id']
        except TypeError:
            self.from_id = event.obj['user_id']

        try:
            self.conversation_message_id = event.message['conversation_message_id']
        except TypeError:
            self.conversation_message_id = event.object['conversation_message_id']

        try:
            self.payload = event.object.get('payload') or {}
        except TypeError:
            self.payload = {}

        self.message_handlers = dict([
            (r'/start', self.start),
            (r'.', self.message)
        ])

        self.chat_message_handlers = dict([
            (r'/sub', self.sub),
            (r'/unsub', self.unsub),
            (r'.', self.chat_message)
        ])

        self.callback = dict([
            ('new_acc', self.new_acc),
            ('ex_acc', self.ex_acc)
        ])
        self.text = None
        self.keyboard = {}
        self.from_user = dict()
        self.chat_title = ''

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
                    return
            self.text = 'I don`t understand you!'
        elif self.event.from_chat:
            for key, func in self.chat_message_handlers.items():
                if re.match(key, self.event.message.text):
                    func()
                    return

    def new_callback_answer(self):
        self.callback.get(self.payload.get('type'))()

    def new_acc(self):
        _uuid = utils.get_uuid()
        if db_persistence.is_exist(vk_id=self.peer_id):
            self.text = vk_dict.ALREADY_EXIST.format(id=_uuid)
            return
        self.text = vk_dict.NEW_ACC_MESSAGE.format(id=_uuid)
        db_persistence.insert_new_connection(_uuid=_uuid, vk_id=self.peer_id, user_name=self.from_user)

    def ex_acc(self):
        self.text = vk_dict.EX_ACC_MESSAGE
        db_persistence.insert_or_update_user_state(self.peer_id, UserState.ID)

    def start(self):
        self.text = vk_dict.START_MESSAGE
        self.keyboard = self.registration_keyboard()

    def sub(self):
        if not db_persistence.is_exist(vk_id=self.from_id):
            self.text = f'@id{self.from_id}\n You are not registered!'
            return
        if db_persistence.is_listening(self.peer_id, self.from_id):
            self.text = f'@id{self.from_id}\n You are already listener of this chat!'
            return
        db_persistence.add_listener(self.peer_id, self.from_id)
        self.text = f'@id{self.from_id}\n I add you to listener of this chat!'

    def unsub(self):
        if not db_persistence.is_exist(vk_id=self.from_id):
            self.text = f'@id{self.from_id}\n You are not registered!'
            return
        if not db_persistence.is_listening(self.peer_id, self.from_id):
            self.text = f'@id{self.from_id}\n You are not listener of this chat!'
            return
        db_persistence.remove_listener(self.peer_id, self.from_id)
        self.text = f'@id{self.from_id}\n I remove you from listener of this chat!'

    def message(self):
        user_state = db_persistence.get_state(self.peer_id)
        if user_state is not None:
            if user_state == UserState.ID:
                try:
                    __uuid = str(uuid.UUID(self.event.message.get('text')))
                    if db_persistence.is_exist(_uuid=__uuid):
                        if not db_persistence.get_ids(_uuid=__uuid)[0][1]:
                            db_persistence.update_connection({'uuid': __uuid},
                                                             {'vkID': self.peer_id, 'user_name': self.from_user})
                            self.text = "Your account is full registered"
                        else:
                            self.text = "This account is already registered!"
                    else:
                        self.text = 'Wrong id! Try again...'
                except ValueError:
                    self.text = 'Wrong id! Try again...'
            else:
                self.text = "Simple message!"
        else:
            self.text = "Simple message!"
        db_persistence.insert_or_update_user_state(self.peer_id, UserState.INITIAL)

    def chat_message(self):
        chat_listeners = db_persistence.get_chat_listeners(self.peer_id)
        if len(chat_listeners) > 0:
            for chat_listener in chat_listeners:
                chat_listener_id = int(chat_listener[0])
                if chat_listener_id != self.from_id:
                    if db_persistence.is_exist(vk_id=chat_listener_id) and db_persistence.is_fully_registered(
                            chat_listener_id):
                        tg_id = db_persistence.get_ids(vk_id=chat_listener_id)[0][2]
                        self.event.client_info.update({'from_title': f'{self.from_user}'})
                        self.event.message.update({'chat_title': self.chat_title})
                        connector.from_vk_to_tg(tg_id, Message.from_vk(self.event))
