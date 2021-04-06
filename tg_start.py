from server import *


def main():
    db_init.main()
    tg_thread = ServerProcess(func=tg_main.main)
    tg_thread.start()
    print('Telegram bot has been started...')


if __name__ == '__main__':
    main()
