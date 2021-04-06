import time
from typing import Callable

from db_module import db_init
from telegram_bot import main as tg_main
from vk_bot import main as vk_main
from multiprocessing import Process
import logging


def try_wrapper(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(e)

    return wrapper


class ServerProcess(Process):

    def __init__(self, func: Callable):
        super().__init__()
        self.func = func
        logging.basicConfig(filename='server.log', level=logging.DEBUG)

    @try_wrapper
    def run(self) -> None:
        self.func()


if __name__ == '__main__':
    db_init.main()
    tg_thread = ServerProcess(func=tg_main.main)
    vk_thread = ServerProcess(func=vk_main.main)

    tg_thread.start()
    vk_thread.start()
