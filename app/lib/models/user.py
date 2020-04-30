# coding: utf-8

import re

from . import power
from app.lib import errors, dbop, cacheop
from app.lib.common import my_md5
from .base import Base

_COMMON_PWD = '123456'


class User(Base):
    def __init__(self):
        self.id = None  # ID
        self.pid = None  # 权限ID
        self.power = None  # 权限ID
        self.sub = None  # 用户标识
        self.pwd = None  # 密码
        self.phone = None  # 介绍
        self.email = None  # 介绍
        self.intro = None  # 介绍
        self.create_time = None  # 创建时间

        self.sid = None  # 对应的sid

    def load(self, kwargs):
        Base.load(self, kwargs)
        if self.pid:
            self.pid = int(self.pid)
            if self.pid in [power.USER, power.ADMIN]:
                self.power = power.POWER_INFO[self.pid]
        return self

    def login(self):
        """
        登录
        :return:
        """
        pwd = my_md5(self.pwd)
        return dbop.check_user(self.sub, pwd)

    def create(self, sub, pid=power.USER):
        """
        创建用户
        :param pid: 
        :param sub: 
        :return: 
        """""
        pwd = my_md5(_COMMON_PWD)
        data = dbop.create_user(pid, sub, pwd)
        if not data:
            return False
        return self.load(data)

    def delete(self):
        """
        删除用户
        :return:
        """
        if not self.sub:
            return False
        res = dbop.delete_user(self.sub)
        if not res:
            return False
        return res

    def get_by_sub(self, sub):
        """
        通过sub的得到user
        :param sub:
        :return:
        """
        data = dbop.get_user_by_sub(sub)
        if not data:
            return False
        return self.load(data)

    def get_list(self, kwargs, page):
        """
        获得user列表
        :param page:
        :param kwargs:
        :return:
        """
        self.load(kwargs)
        res = dbop.get_user_list(kwargs, page)
        if not res:
            return False
        return res

    def get_list_num(self, kwargs):
        """
        获得user列表
        :param kwargs:
        :return:
        """
        self.load(kwargs)
        res = dbop.get_user_list_num(kwargs)
        if not res:
            return 0
        return res

    def update_profile(self):
        """
        更新个人信息
        :return:
        """
        if not self.sub:
            return False
        kwargs = {}
        if self.phone:
            kwargs['phone'] = self.phone
        if self.email:
            kwargs['email'] = self.email
        if self.intro:
            kwargs['intro'] = self.intro
        res = dbop.update_user_profile(self.sub, kwargs)
        if not res:
            return False
        return res

    def change_power(self):
        """
        更新个人信息
        :return:
        """
        if not self.pid:
            return False
        res = dbop.change_user_power(self.sub, self.pid)
        if not res:
            return False
        return True

    def reset_pwd(self, new_pwd):
        """
        设置密码
        :return:
        """
        if not dbop.check_user(self.sub, self.pwd):
            return False
        res = dbop.reset_user_pwd(self.sub, my_md5(new_pwd))
        if not res:
            return False
        self.pwd = new_pwd
        return True

    def check_arrt(self):
        if self.phone:
            if not re.match(r"^1[35678]\d{9}$", self.phone):
                return False, '手机号格式错误'
        else:
            return False, '手机号不能为空'
        if self.email:
            if not re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", self.email):
                return False, '邮箱地址格式错误'
        else:
            return False, '邮箱地址不能为空'
        return True, ''

    def set_ws_sid(self, sid):
        res = cacheop.set_user_map(self.sub, sid)
        if not res:
            return False
        return True

    def get_ws_sid(self):
        res = cacheop.get_user_map(self.sub)
        if not res:
            return False
        return res

    def del_ws_sid(self):
        res = cacheop.del_user_map(self.sub)
        if not res:
            return False
        return res
