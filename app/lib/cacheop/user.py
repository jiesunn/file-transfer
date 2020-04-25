# coding: utf-8

from . import Redis

_REDIS = Redis().POOL

_USER_MAP = 'USERMAP'


def set_user_map(sub=None, sid=None):
    if sub is None or sid is None:
        return False
    return _REDIS.hset(_USER_MAP, sub, sid)


def get_user_map(sub=None):
    if sub is None:
        return False
    return _REDIS.hget(_USER_MAP, sub)


def del_user_map(sub=None):
    if sub is None:
        return False
    return _REDIS.hdel(_USER_MAP, sub)

