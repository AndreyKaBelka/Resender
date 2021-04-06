from db_module import db_init
from telegram_bot import main as tg_main
from vk_bot import main as vk_main
from multiprocessing import Process

if __name__ == '__main__':
    db_init.main()
    tg_thread = Process(target=tg_main.main)
    vk_thread = Process(target=vk_main.main)

    tg_thread.start()
    vk_thread.start()
