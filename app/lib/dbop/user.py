# coding: utf-8

import datetime

import pymysql

from . import MysqlPool


def create_user(pid, sub, pwd):
    """
    创建用户
    :param pid:
    :param sub:
    :param pwd:
    :return:
    """
    mp = MysqlPool()
    sql = ('INSERT INTO users'
           '(pid, sub, pwd, create_time) '
           'VALUE (%s, %s, %s, %s)')
    now = datetime.datetime.now()
    user_id = mp.insert(sql, [pid, sub, pwd, now])
    if not user_id:
        return False
    return {'id': user_id, 'pid': pid,
            'sub': sub, 'pwd': pwd,
            'create_time': now
            }


def get_user_list(kwargs, page, count=10):
    mp = MysqlPool()
    start = str((int(page) - 1) * count)
    sql = "SELECT * FROM users WHERE 1=1"
    for key, value in kwargs.items():
        sql += " AND " + key + "='" + value + "'"
    sql += " ORDER BY id DESC LIMIT " + start + "," + str(count)
    res = mp.fetch_all(sql, [])
    if not res:
        return False
    return res


def get_user_list_num(kwargs):
    mp = MysqlPool()
    sql = "SELECT count(*) as num FROM users WHERE 1=1"
    for key, value in kwargs.items():
        sql += " AND " + key + "='" + value + "'"
    res = mp.fetch_one(sql, [])
    if not res:
        return False
    return res['num']


def check_user(sub, pwd):
    """
    验证账号密码
    :param sub:
    :param pwd:
    :return:
    """
    mp = MysqlPool()
    sql = "SELECT * FROM users WHERE sub=%s and pwd=%s"
    res = mp.fetch_one(sql, [sub, pwd])
    if not res:
        return False
    return res


def get_user_by_sub(sub):
    """
    通过账号获取用户
    :param sub:
    :return:
    """
    mp = MysqlPool()
    sql = "SELECT * FROM users WHERE sub=%s"
    res = mp.fetch_one(sql, [sub])
    if not res:
        return False
    return res


def update_user_profile(sub, kwargs):
    """
    更新个人信息
    :param sub:
    :param kwargs:
    :return:
    """
    mp = MysqlPool()
    sql = "UPDATE users SET sub=%s"
    for key, value in kwargs.items():
        sql += ", " + key + "='" + value + "'"
    sql += " WHERE sub=%s"
    res = mp.update(sql, [sub, sub])
    if not res:
        return False
    return res


def reset_user_pwd(sub, pwd):
    """
    重设密码
    :param sub:
    :param pwd:
    :return:
    """
    mp = MysqlPool()
    sql = 'UPDATE users SET pwd=%s WHERE sub=%s'
    res = mp.update(sql, [pwd, sub])
    if not res:
        return False
    return res


def change_user_power(sub, pid):
    """
    更改权限
    :param sub:
    :param pid:
    :return:
    """
    mp = MysqlPool()
    sql = 'UPDATE users SET pid=%s WHERE sub=%s'
    res = mp.update(sql, [pid, sub])
    if not res:
        return False
    return res


def delete_user(sub):
    """
    删除用户
    :param sub:
    :return:
    """
    mp = MysqlPool()
    sql = 'DELETE FROM users WHERE sub=%s'
    res = mp.delete(sql, [sub])
    if not res:
        return False
    return res
