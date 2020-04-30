# coding: utf-8

import os
import pymysql
from redis import StrictRedis

BASEDIR = os.path.abspath(os.path.dirname(__file__))
ENV = 'development'


class Config:
    TEMPLATE_FOLDER = './templates'
    STATIC_FOLDER = './static'
    ASYNC_MODE = None


class DevelopmentConfig(Config):
    """
    开发环境
    """

    DEBUG = True  # 是否开启Debug模式

    # Redis
    REDIS_HOST = '172.17.0.2'
    REDIS_PORT = 6379
    REDIS_POOL = {
        'host': REDIS_HOST,
        'port': REDIS_PORT,
        'socket_timeout': 5,
        'socket_connect_timeout': 2,
        'max_connections': 5,
        'decode_responses': True,
    }

    # MySQL
    MYSQL_POOL = {
        'creator': pymysql,
        'host': '172.17.0.3',
        'port': 3306,
        'user': 'root',
        'password': 'file-transfer',
        'database': 'file_transfer',
        'charset': 'utf8',
        'maxconnections': 6,  # 连接池允许的最大连接数
        'mincached': 2,  # 初始化时，链接池中至少创建的空闲的链接
        'maxcached': 5,  # 链接池中最多闲置的链接
        'maxshared': 3,  # 链接池中最多共享的链接
    }

    # Session
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True  # 是否强制加盐，混淆session
    SECRET_KEY = 'secret key'  # 如果加盐，那么必须设置的安全码，盐
    # sessons是否长期有效，false，则关闭浏览器，session失效
    SESSION_PERMANENT = False
    # session长期有效，则设定session生命周期，整数秒
    # ERMANENT_SESSION_LIFETIME = 24 * 60 * 60
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


class TestingConfig(Config):
    """
    测试环境
    """
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """
    生产环境
    """
    DEBUG = False  # 是否开启Debug模式


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
