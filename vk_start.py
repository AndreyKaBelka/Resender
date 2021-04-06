from server import *


def main():
    vk_thread = ServerProcess(func=vk_main.main)
    vk_thread.start()
    print('Vk bot has been started...')


if __name__ == '__main__':
    main()
