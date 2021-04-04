import pymysql
import os
from dotenv import load_dotenv
from abc import ABCMeta, abstractmethod

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
    def add_query(self, value: str, arg: any) -> 'QueryBuilder':
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


class UpdateQueryBuilder(QueryBuilder):
    def __init__(self):
        self.update_vals = []
        self.args = []

    def add_query(self, value: str, arg: any) -> QueryBuilder:
        if arg is not None:
            self.update_vals.append(value + ' = {!r}')
            self.args.append(str(arg))
        return self

    def build(self) -> str:
        return str.join(" , ", self.update_vals).format(*self.args)


def insert_new_connection(_uuid=None, vk_id=None, tg_id=None):
    if _uuid is None and vk_id is None and tg_id is None:
        raise AttributeError("All arguments can't be None!")
    insert_query = InsertQueryBuilder() \
        .add_query('uuid', _uuid) \
        .add_query('vkID', vk_id) \
        .add_query('tgID', tg_id) \
        .build()
    insert_into_table('resender.connection', insert_query)


def get_ids(_uuid=None, vk_id=None, tg_id=None) -> list:
    if _uuid is None and vk_id is None and tg_id is None:
        raise AttributeError("All arguments can't be None!")
    where_query = WhereQueryBuilder() \
        .add_query('uuid', _uuid) \
        .add_query('vkID', vk_id) \
        .add_query('tgID', tg_id) \
        .build()
    res = select_from_table('resender.connection', where_query)
    return res


def update_connection(where_args: dict, update_args: dict):
    if where_args.get('uuid') is None and where_args.get('vkID') is None and where_args.get('tgID') is None:
        raise AttributeError("All arguments can't be None!")
    update_query = UpdateQueryBuilder() \
        .add_query('uuid', update_args.get('uuid')) \
        .add_query('vkID', update_args.get('vkID')) \
        .add_query('tgID', update_args.get('tgID')) \
        .build()
    where_query = WhereQueryBuilder() \
        .add_query('uuid', where_args.get('uuid')) \
        .add_query('vkID', where_args.get('vkID')) \
        .add_query('tgID', where_args.get('tgID')) \
        .build()
    update_in_table('resender.connection', update_query, where_query)


def is_exist(_uuid=None, vk_id=None, tg_id=None) -> bool:
    return True if len(get_ids(_uuid, vk_id, tg_id)) > 0 else False


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


def update_in_table(table_name: str, update_query: str, where_query: str):
    if where_query is None:
        raise AttributeError('where_query shouldn`t be None!')
    query = f"""
    UPDATE {table_name}
    SET {update_query}
    WHERE {where_query}
    """
    cur.execute(query)
    con.commit()