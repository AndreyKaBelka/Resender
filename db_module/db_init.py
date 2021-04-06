import sqlite3
from sqlite3 import Error
from dotenv import load_dotenv
import os

load_dotenv()


class DbSettings:
    HOST_NAME = os.getenv('HOST_NAME')
    USER_PASS = os.getenv('USER_PASS')
    USER_NAME = os.getenv('USER_NAME')
    SQL_NAME = os.getenv('SQL_NAME')


def sql_connection():
    try:
        return sqlite3.connect(DbSettings.SQL_NAME + '.db', check_same_thread=False)
    except Error:
        print(Error)


def main():
    con = sql_connection()
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS `chat_listeners` (
      `chat_id` int NOT NULL,
      `user_id` varchar(45) NOT NULL,
      PRIMARY KEY (`chat_id`,`user_id`)
    );""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS  `vk_finite_state` (
      `user_id` int unsigned NOT NULL UNIQUE,
      `finite_state` int NOT NULL DEFAULT '0',
      PRIMARY KEY (`user_id`)
    );""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS `tg_finite_state` (
      `tg_id` int unsigned NOT NULL UNIQUE ,
      `state` int unsigned NOT NULL DEFAULT '0',
      PRIMARY KEY (`tg_id`)
    );""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS `connection` (
      `UUID` varchar(36) NOT NULL UNIQUE ,
      `vkID` int unsigned DEFAULT NULL UNIQUE ,
      `tgID` int unsigned DEFAULT NULL UNIQUE ,
      `user_name` varchar(45) DEFAULT NULL,
      PRIMARY KEY (`UUID`)
    );""")
    con.commit()
