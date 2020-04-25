# coding: utf-8

from datetime import datetime

from . import Redis

_REDIS = Redis().POOL

_LOG = 'LOG'
_LOG_KEY = 'LOG_%s'


def set_log(data=None):
    if not data:
        return False
    now = datetime.now().date()
    key = _REDIS.incr(_LOG_KEY % now, 1)
    return _REDIS.hset(_LOG, key, data)


def get_log_list():
    return _REDIS.hgetall(_LOG)


def del_log_list(keys=None):
    if not keys:
        return False
    for key in keys:
        _REDIS.hdel(_LOG, key)
    return True


def del_log_key(date):
    if not date:
        return False
    key = _LOG_KEY % date
    return _REDIS.delete(key)
