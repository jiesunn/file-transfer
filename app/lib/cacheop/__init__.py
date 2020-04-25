# coding: utf-8

"""
  Redis相关操作的封装。
"""

from redis import ConnectionPool, Redis as LibRedis

from app import my_config


class Redis(object):
    def __init__(self, decode=True):
        _REDIS = my_config.REDIS_POOL
        _POOL = ConnectionPool(
            host=_REDIS['host'],
            port=_REDIS['port'],
            socket_timeout=_REDIS['socket_timeout'],
            socket_connect_timeout=_REDIS['socket_connect_timeout'],
            max_connections=_REDIS['max_connections'],
            decode_responses=decode)
        self.POOL = LibRedis(
            connection_pool=_POOL
        )


# import method from submodule
from .user import *
from .file import *
from .log import *
