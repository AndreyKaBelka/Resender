from server import *


@try_wrapper
def main():
    tg_main.main()
    print('Telegram bot has been started...')


if __name__ == '__main__':
    main()
