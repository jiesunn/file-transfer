# coding: utf-8


class Code(object):
    """
    处理请求的通用组件
    """

    def __init__(self):
        self.ERROR = -1  # 错误
        self.SUCCESS = 200  # 成功
        self.STAY_BY = 0  # 待命
        self.BEING = 100  # 正在传输
        self.PAUSE = 101  # 暂停传输


class State(object):
    """
    文件传输状态码
    """

    def __init__(self):
        self.NORMAL = 0  # 正常
        self.PAUSE = 1  # 暂停
        self.INTERRUPT = -1  # 中断


CODE = Code()
STATE = State()
