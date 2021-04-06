import uuid
from typing import List
import vk_bot

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class TgUserState:
    INITIAL = 0
    CHAT = 1
    MESSAGE = 2


def get_uuid():
    return uuid.uuid4()


def get_keyboard_for_chats(chats: list, page_num: int):
    max_size = 3
    navigation_btns = [InlineKeyboardButton('⬅', callback_data=f'bck:{page_num}'),
                       InlineKeyboardButton('➡', callback_data=f'fwd:{page_num}')]
    max_page_counts = len(chats) // max_size + (1 if len(chats) % max_size else 0)
    if page_num <= 1:
        page_num = 1
        navigation_btns.pop(0)
    elif page_num >= max_page_counts:
        page_num = max_page_counts
        navigation_btns.pop(1)
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*get_paginating_keyboard_button(chats, page_num, max_size))
    markup.row(*navigation_btns)
    return markup


def get_paginating_keyboard_button(chats: list, page_num: int, max_size: int) -> List[InlineKeyboardButton]:
    res = []
    bottom_level = max_size * (page_num - 1)
    top_level = max_size * page_num if max_size * page_num < len(chats) else len(chats)
    for i in range(bottom_level, top_level):
        chat_title = vk_bot.loop.run_until_complete(vk_bot.get_chat_title(peer_id=chats[i]))
        res.append(InlineKeyboardButton(chat_title, callback_data=chats[i]))
    return res
