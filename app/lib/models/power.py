# coding: utf-8

from .base import Base

USER = 1
ADMIN = 2
POWER_INFO = {
    USER: 'user',
    ADMIN: 'admin',
}


class Power(Base):
    def __init__(self):
        self.id = None  # ID
        self.info = None  # 权限信息

    def load(self, **kwargs):
        Base.load(self, **kwargs)
        return self
