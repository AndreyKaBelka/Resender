from typing import Callable

from db_module import db_init
from telegram_bot import main as tg_main
from vk_bot import main as vk_main
from multiprocessing import Process


def try_wrapper(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(e)

    return wrapper


class ServerProcess(Process):

    def __init__(self, func: Callable, args=()):
        super().__init__()
        self.func = func
        self.args = args

    @try_wrapper
    def run(self) -> None:
        self.func()


if __name__ == '__main__':
    db_init.main()
    tg_thread = ServerProcess(func=tg_main.main)
    vk_thread = ServerProcess(func=vk_main.main)

    print('App is starting...')
    vk_thread.start()
    print('Vk bot has been started...')
    tg_thread.start()
    print('Telegram bot has been started...')
