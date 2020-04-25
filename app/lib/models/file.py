# coding: utf-8

import struct
import json

from .. import cacheop
from .base import Base


class File(Base):
    def __init__(self):
        self.id = None  # ID
        self.name = None  # 文件名
        self.size = None  # 文件名
        self.state = None  # 状态
        self.cur = None  # 状态
        self.receiver = None  # 接收方
        self.sender = None  # 发送方
        self.desc = None

        self.start = None  # 开始位置
        self.length = None  # 长度
        self.data = None

    def load(self, kwargs):
        Base.load(self, kwargs)
        return self

    def unpack(self, data):
        """
        解包（循环3次，分别取 fileID start length）
        :param data:
        :return:
        """
        process_len = 0
        for i in range(0, 3):
            # 获取字符串长度
            temp = data[process_len:(process_len + 1)]
            process_len += 1
            str_len = struct.unpack('b', temp)[0]

            # 获取字符串
            arr = []
            for j in range(0, str_len):
                temp = data[process_len:(process_len + 1)]
                process_len += 1
                arr.append(chr(struct.unpack('b', temp)[0]))
            string = ''.join(arr)

            # 分别赋值
            if i is 0:
                self.id = string
                self.get_desc()
            elif i is 1:
                self.start = string
                self.cur = string
            elif i is 2:
                self.length = string
        self.data = data[process_len:]
        self.set_desc()

    def get_desc(self):
        if not self.id:
            return False
        res = cacheop.get_file_desc(self.id)
        if not res:
            return False
        return self.load(json.loads(res))

    def set_desc(self):
        if not self.desc:
            self.desc = json.dumps({
                'id': self.id,
                'name': self.name,
                'size': self.size,
                'state': self.state,
                'cur': self.cur,
                'sender': self.sender,
                'receiver': self.receiver,
            })
        res = cacheop.set_file_desc(self.id, self.desc)
        if not res:
            return False
        return True

    def del_desc(self):
        res = cacheop.del_file_desc(self.id)
        if not res:
            return False
        return True

    def get_data(self):
        data, length = cacheop.get_file_data(self.id, self.start)
        if not data or not length:
            return False, False
        return data, length

    def set_data(self):
        res = cacheop.set_file_data(self.id, self.start, self.data, self.length)
        if not res:
            return False
        return True

    def del_data(self):
        res = cacheop.del_file_data(self.id, self.start)
        if not res:
            return False
        return True

    @staticmethod
    def get_desc_list():
        res = cacheop.get_file_desc_list()
        if not res:
            return False
        return res
