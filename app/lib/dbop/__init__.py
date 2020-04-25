# coding: utf-8

import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection

from app import my_config


class MysqlPool(object):
    """
    MySQL连接池
    """

    def __init__(self):
        _MYSQL = my_config.MYSQL_POOL
        self.POOL = PooledDB(creator=_MYSQL['creator'],
                             host=_MYSQL['host'],
                             port=_MYSQL['port'],
                             user=_MYSQL['user'],
                             password=_MYSQL['password'],
                             database=_MYSQL['database'],
                             charset=_MYSQL['charset'],
                             mincached=_MYSQL['mincached'],
                             maxcached=_MYSQL['maxcached'],
                             maxshared=_MYSQL['maxshared'])

    def __new__(cls, *args, **kw):
        """
        启用单例模式
        :param args:
        :param kw:
        :return:
        """
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def connect(self):
        """
        启动连接
        :return:
        """
        conn = self.POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def connect_close(self, conn, cursor):
        """
        关闭连接
        :param conn:
        :param cursor:
        :return:
        """
        cursor.close()
        conn.close()
        self.POOL = None

    def fetch_one(self, sql, args):
        """
        查询单条数据
        :param sql:
        :param args:
        :return:
        """
        conn, cursor = self.connect()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        self.connect_close(conn, cursor)
        return result

    def fetch_all(self, sql, args):
        """
        批量查询
        :param sql:
        :param args:
        :return:
        """
        conn, cursor = self.connect()
        cursor.execute(sql, args)
        record_list = cursor.fetchall()
        self.connect_close(conn, cursor)
        return record_list

    def insert(self, sql, args):
        """
        新增数据
        :param sql:
        :param args:
        :return:
        """
        return self.execute(sql, args)

    def insert_many(self, sql, args):
        """
        批量新增数据
        :param sql:
        :param args:
        :return:
        """
        return self.execute_many(sql, args)

    def update(self, sql, args):
        """
        更新数据
        :param sql:
        :param args:
        :return:
        """
        return self.execute(sql, args)

    def delete(self, sql, args):
        """
        删除数据
        :param sql:
        :param args:
        :return:
        """
        return self.execute(sql, args)

    def execute(self, sql, args):
        """
        执行单条写入操作
        :param sql:
        :param args:
        :return:
        """
        conn, cursor = self.connect()
        row = cursor.execute(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row

    def execute_many(self, sql, args):
        """
        执行批量写入操作
        :param sql:
        :param args:
        :return:
        """
        conn, cursor = self.connect()
        row = cursor.executemany(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row


# import method from submodule
from .user import *
from .log import *
