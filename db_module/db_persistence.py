import pymysql
import os
from dotenv import load_dotenv
from abc import ABCMeta, abstractmethod
import uuid

load_dotenv()


class DbSettings:
    HOST_NAME = os.getenv('HOST_NAME')
    USER_PASS = os.getenv('USER_PASS')
    USER_NAME = os.getenv('USER_NAME')
    SQL_NAME = os.getenv('SQL_NAME')


con = pymysql.connect(host=DbSettings.HOST_NAME, user=DbSettings.USER_NAME, password=DbSettings.USER_PASS,
                      database=DbSettings.SQL_NAME)
cur = con.cursor()


class QueryBuilder:
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_query(self, value: str, arg: any):
        """ Добавить значение переменной и аргумент в query """

    @abstractmethod
    def build(self) -> str:
        """ Построить query """


class WhereQueryBuilder(QueryBuilder):
    def __init__(self):
        self.wheres = []
        self.args = []

    def add_query(self, value: str, arg: any) -> QueryBuilder:
        if arg is not None:
            self.wheres.append(value + " = {!r}")
            self.args.append(arg)
        return self

    def build(self) -> str:
        return str.join(" AND ", self.wheres).format(*self.args)


class InsertQueryBuilder(QueryBuilder):
    def __init__(self):
        self.values = []
        self.args = []

    def add_query(self, value: str, arg: any = None) -> QueryBuilder:
        if arg is not None:
            self.values.append(value)
            self.args.append(arg)
        return self

    def build(self) -> str:
        return '({!s}) VALUES ({!s})'.format(str.join(',', self.values),
                                             str.join(',', ['{!r}'.format(str(arg)) for arg in self.args]))


def get_ids(uuid=None, vk_id=None, tg_id=None):
    if uuid is None and vk_id is None and tg_id is None:
        raise AttributeError("All arguments can't be None!")
    where_query = WhereQueryBuilder() \
        .add_query('uuid', uuid) \
        .add_query('vkID', vk_id) \
        .add_query('tgID', tg_id) \
        .build()
    res = select_from_table('resender.connection', where_query)
    print(res[0])


def select_from_table(table_name: str, where_query: str, args_to_select: list = None) -> list:
    query = f"""
    SELECT {str.join(",", args_to_select) if args_to_select is not None else "*"}
    FROM {table_name}
    WHERE {where_query}
    """
    cur.execute(query)
    return cur.fetchall()


def insert_into_table(table_name: str, query: str):
    cur.execute(f"""INSERT INTO {table_name}{query}""")
    con.commit()
