# coding: utf-8

from . import MysqlPool


def insert_logs(data):
    """
    新建日志
    :param data:
    :return:
    """
    mp = MysqlPool()
    sql = "INSERT INTO logs(`level`, `code`, `method`, path, params, response, user_ip, request_time) VALUE"
    for key, item in data.items():
        sql += " ('" + item['level'] + "', "
        sql += "'" + str(item['code']) + "', "
        sql += "'" + item['method'] + "', "
        sql += "'" + item['path'] + "', "
        sql += "'" + item['params'] + "', "
        sql += "'" + item['response'] + "', "
        sql += "'" + item['user_ip'] + "', "
        sql += "'" + item['request_time'] + "'),"
    sql = sql[:-1]
    return mp.insert(sql, [])


def get_log_list(kwargs, page, count=10):
    """
    获取日志列表
    :param kwargs:
    :param page:
    :param count:
    :return:
    """
    mp = MysqlPool()
    start = str((int(page) - 1) * count)
    sql = "SELECT * FROM logs WHERE 1=1"
    for key, value in kwargs.items():
        sql += " AND " + key + "='" + value + "'"
    sql += " ORDER BY id DESC LIMIT " + start + "," + str(count)
    res = mp.fetch_all(sql, [])
    if not res:
        return False
    return res


def get_log_list_num(kwargs):
    """
    获取日志列表的数量
    :param kwargs:
    :return:
    """
    mp = MysqlPool()
    sql = "SELECT count(*) as num FROM logs WHERE 1=1"
    for key, value in kwargs.items():
        sql += " AND " + key + "='" + value + "'"
    res = mp.fetch_one(sql, [])
    if not res:
        return False
    return res['num']

