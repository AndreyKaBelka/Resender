from abc import ABCMeta, abstractmethod
from db_module.db_init import *

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


def insert_new_connection(_uuid=None, vk_id=None, tg_id=None, user_name=None):
    if _uuid is None and vk_id is None and tg_id is None:
        raise AttributeError("All arguments can't be None!")
    insert_query = InsertQueryBuilder() \
        .add_query('uuid', _uuid) \
        .add_query('vkID', vk_id) \
        .add_query('tgID', tg_id) \
        .add_query('user_name', user_name) \
        .build()
    insert_into_table('connection', insert_query)


def insert_or_update_tg_state(tg_id, state=0):
    insert_query = InsertQueryBuilder() \
        .add_query('tg_id', tg_id) \
        .add_query('state', state) \
        .build()
    update_query = UpdateQueryBuilder() \
        .add_query('state', state) \
        .build()
    __insert_into_table_on_duplicate_update('tg_finite_state', insert_query, update_query, 'tg_id')


def get_tg_state(tg_id):
    where_query = WhereQueryBuilder() \
        .add_query('tg_id', tg_id) \
        .build()
    res = select_from_table('tg_finite_state', where_query)
    return res[0][1] if len(res) > 0 else None


def insert_or_update_user_state(user_id, state=0):
    insert_query = InsertQueryBuilder() \
        .add_query('user_id', user_id) \
        .add_query('finite_state', state) \
        .build()
    update_query = UpdateQueryBuilder() \
        .add_query('finite_state', state) \
        .build()
    __insert_into_table_on_duplicate_update('vk_finite_state', insert_query, update_query, 'user_id')


def get_ids(_uuid=None, vk_id=None, tg_id=None) -> list:
    if _uuid is None and vk_id is None and tg_id is None:
        raise AttributeError("All arguments can't be None!")
    where_query = WhereQueryBuilder() \
        .add_query('uuid', _uuid) \
        .add_query('vkID', vk_id) \
        .add_query('tgID', tg_id) \
        .build()
    res = select_from_table('connection', where_query)
    return res


def update_connection(where_args: dict, update_args: dict):
    if where_args.get('uuid') is None and where_args.get('vkID') is None and where_args.get('tgID') is None:
        raise AttributeError("All arguments can't be None!")
    update_query = UpdateQueryBuilder() \
        .add_query('uuid', update_args.get('uuid')) \
        .add_query('vkID', update_args.get('vkID')) \
        .add_query('tgID', update_args.get('tgID')) \
        .add_query('user_name', update_args.get('user_name')) \
        .build()
    where_query = WhereQueryBuilder() \
        .add_query('uuid', where_args.get('uuid')) \
        .add_query('vkID', where_args.get('vkID')) \
        .add_query('tgID', where_args.get('tgID')) \
        .build()
    update_in_table('connection', update_query, where_query)


def add_listener(chat_id, user_id):
    insert_query = InsertQueryBuilder() \
        .add_query('chat_id', chat_id) \
        .add_query('user_id', user_id) \
        .build()
    insert_into_table('chat_listeners', insert_query)


def remove_listener(chat_id, user_id):
    where_query = WhereQueryBuilder() \
        .add_query('chat_id', chat_id) \
        .add_query('user_id', user_id) \
        .build()
    delete_from_table('chat_listeners', where_query)


def get_chat_listeners(chat_id) -> list:
    where_query = WhereQueryBuilder() \
        .add_query('chat_id', chat_id) \
        .build()
    return select_from_table('chat_listeners', where_query, ["user_id"])


def get_listener_chats_from_tg(tg_id):
    where_query = WhereQueryBuilder() \
        .add_query('tgID', tg_id) \
        .build()
    res = select_from_table('connection', where_query, ['vkID'])
    vk_id = res[0][0] if len(res) > 0 else None
    if vk_id is not None:
        where_query = WhereQueryBuilder() \
            .add_query('user_id', vk_id) \
            .build()
        chats = select_from_table('chat_listeners', where_query, ['chat_id'])
        return [chat[0] for chat in chats]
    else:
        return None


def get_username_from_tg(tg_id):
    where_query = WhereQueryBuilder() \
        .add_query('tgID', tg_id) \
        .build()
    res = select_from_table('connection', where_query, ['user_name'])
    return res[0][0] if len(res) > 0 else None


def is_listening(chat_id, user_id):
    where_query = WhereQueryBuilder() \
        .add_query('chat_id', chat_id) \
        .add_query('user_id', user_id) \
        .build()
    return True if len(select_from_table('chat_listeners', where_query)) > 0 else False


def is_exist(_uuid=None, vk_id=None, tg_id=None) -> bool:
    return True if len(get_ids(_uuid, vk_id, tg_id)) > 0 else False


def get_state(user_id) -> int:
    where_query = WhereQueryBuilder() \
        .add_query('user_id', user_id) \
        .build()
    res = select_from_table('vk_finite_state', where_query)
    return res[0][1] if len(res) > 0 else None


def select_from_table(table_name: str, where_query: str, args_to_select: list = None) -> list:
    with sql_connection() as con:
        cur = con.cursor()
        query = f"""
        SELECT {str.join(",", args_to_select) if args_to_select is not None else "*"}
        FROM {table_name}
        WHERE {where_query}
        """
        cur.execute(query)
        return cur.fetchall()


def is_fully_registered(vk_id=None, tg_id=None) -> bool:
    where_query = WhereQueryBuilder() \
        .add_query('vkID', vk_id) \
        .add_query('tgID', tg_id) \
        .build()
    res = select_from_table('connection', where_query)
    return True if len(res) > 0 and res[0][1] and res[0][2] else False


def insert_into_table(table_name: str, query: str):
    with sql_connection() as con:
        cur = con.cursor()
        cur.execute(f"""INSERT INTO {table_name}{query}""")
        con.commit()


def update_in_table(table_name: str, update_query: str, where_query: str):
    with sql_connection() as con:
        cur = con.cursor()
        if where_query is None:
            raise AttributeError('where_query shouldn`t be None!')
        query = f"""
        UPDATE {table_name}
        SET {update_query}
        WHERE {where_query}
        """
        cur.execute(query)
        con.commit()


def delete_from_table(table_name: str, where_query: str):
    with sql_connection() as con:
        cur = con.cursor()
        query = f"""
        DELETE FROM {table_name}
        WHERE {where_query}
        """
        cur.execute(query)
        con.commit()


def __insert_into_table_on_duplicate_update(table_name: str, insert_query: str, update_query: str, on_conflict=None):
    with sql_connection() as con:
        cur = con.cursor()
        cur.execute(f"""INSERT INTO {table_name}{insert_query} ON CONFLICT({on_conflict}) DO UPDATE SET {update_query}""")
        con.commit()
