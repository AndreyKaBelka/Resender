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

    def __init__(self, func: Callable):
        super().__init__()
        self.func = func

    @try_wrapper
    def run(self) -> None:
        self.func()


if __name__ == '__main__':
    db_init.main()
    tg_thread = ServerProcess(func=tg_main.main)
    vk_thread = ServerProcess(func=vk_main.main)

    tg_thread.start()
    print('*****************\nTelegram bot has been started...\n*****************')
    print('*****************\nVk bot is starting..\n*****************')
    vk_thread.start()
    print('*****************\nVk bot has been started...\n*****************')
