import json

from .. import cacheop, dbop
from .base import Base


class Log(Base):
    def __init__(self):
        self.id = None  # ID
        self.level = None  # 日志等级
        self.code = None  # HTTP CODE
        self.method = None  # 请求类型
        self.path = None  # 请求地址
        self.params = None  # 请求参数
        self.response = None  # 返回内容
        self.user_ip = None  # 用户IP
        self.request_time = None  # 请求时间

    def load(self, kwargs):
        Base.load(self, kwargs)
        return self

    def set(self):
        """
        在缓存中设置log
        :return:
        """
        data = {
            'level': self.level,
            'method': self.method,
            'code': self.code,
            'path': self.path,
            'params': self.params,
            'response': self.response,
            'user_ip': self.user_ip,
            'request_time': self.request_time,
        }
        res = cacheop.set_log(json.dumps(data))
        if not res:
            return False
        return res

    @staticmethod
    def get_list():
        """
        从缓存中得到log列表
        :return:
        """
        log_list = cacheop.get_log_list()
        return log_list

    @staticmethod
    def del_list(keys):
        """
        删除缓存log列表
        :param keys:
        :return:
        """
        if not keys:
            return False
        res = cacheop.del_log_list(keys)
        if not res:
            return False
        return res

    @staticmethod
    def del_date_key(date):
        """
        删除缓存date key
        :param date:
        :return:
        """
        if not date:
            return False
        res = cacheop.del_log_key(date)
        if not res:
            return False
        return res

    @staticmethod
    def save_list(data=None):
        """
        保存到数据库
        :param data:
        :return:
        """
        if not data:
            return False
        res = dbop.insert_logs(data)
        if not res:
            return False
        return res

    def query_list(self, kwargs, page):
        """
        从数据库查询
        :param kwargs:
        :param page:
        :return:
        """
        self.load(kwargs)
        res = dbop.get_log_list(kwargs, page)
        if not res:
            return False
        return res

    def query_list_num(self, kwargs):
        """
        从数据库查询
        :param kwargs:
        :return:
        """
        self.load(kwargs)
        res = dbop.get_log_list_num(kwargs)
        if not res:
            return 0
        return res
