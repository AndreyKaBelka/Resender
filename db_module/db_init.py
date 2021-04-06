import os
import urllib.parse as urlparse

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DbSettings:
    HOST_NAME = os.getenv('HOST_NAME')
    USER_PASS = os.getenv('USER_PASS')
    USER_NAME = os.getenv('USER_NAME')
    SQL_NAME = os.getenv('SQL_NAME')
    DB_TYPE = os.getenv('DB_TYPE')
    POSTGRES_URL = os.environ['DATABASE_URL']

    @staticmethod
    def get_psql_params():
        url = urlparse.urlparse(DbSettings.POSTGRES_URL)
        return {'dbname': url.path[1:],
                'user': url.username,
                'password': url.password,
                'host': url.hostname,
                'port': url.port}


def sql_connection():
    try:
        return psycopg2.connect(**DbSettings.get_psql_params())
    except Exception as e:
        print(e)


def main():
    con = sql_connection()
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS chat_listeners (
      chat_id int NOT NULL,
      user_id int NOT NULL,
      PRIMARY KEY (chat_id,user_id)
    );""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS  vk_finite_state (
      user_id int NOT NULL UNIQUE,
      finite_state int NOT NULL DEFAULT '0',
      PRIMARY KEY (user_id)
    );""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS tg_finite_state (
      tg_id int NOT NULL UNIQUE ,
      state int NOT NULL DEFAULT '0',
      PRIMARY KEY (tg_id)
    );""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS connection (
      UUID varchar(36) NOT NULL UNIQUE ,
      vkID int DEFAULT NULL UNIQUE ,
      tgID int DEFAULT NULL UNIQUE ,
      user_name varchar(45) DEFAULT NULL,
      PRIMARY KEY (UUID)
    );""")
    con.commit()


if __name__ == '__main__':
    main()
