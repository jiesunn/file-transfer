# coding: utf-8

import logging


class ErrorReason(object):
    """
    异常原因代码
    """

    def __init__(self, code, message, log_level=logging.ERROR):
        self.code = code
        self._message = message
        self.log_level = log_level

    @property
    def message(self):
        return getattr(__builtin__, '_')(self._message)


'''
错误码是4位数的整数，前两位表示错误的类型(从10开始)，后两位表示具体的错误
code相同表示错误不关注code，只关注message
分类：
    1000: 因用户输出导致的异常(WARNING)
    13XX: 用户系统异常(WARNING)
    4000: 业务逻辑异常(ERROR)
    50XX: 系统内部异常(ERROR)
'''

# 请求参数错误
BAD_REQ_ERROR = ErrorReason(1001, '非法请求', log_level=logging.WARNING)
REQ_METHOD_ERROR = ErrorReason(1002, u'请求方法不允许', log_level=logging.WARNING)
REQ_PARAMS_ERROR = ErrorReason(1003, u'用户请求参数错误', log_level=logging.WARNING)
REQ_SIGN_ERROR = ErrorReason(1004, u'请求签名错误', log_level=logging.WARNING)
PERMISSION_ERROR = ErrorReason(1005, u'权限操作异常', log_level=logging.WARNING)

##########################
# 帐号输入格式错误
##########################
USERNAME_NOT_START_WITH_LETTER = ErrorReason(
    1000, '用户名必须以字母开头', log_level=logging.WARNING)
USERNAME_LENGTH_ERROR = ErrorReason(
    1000, '用户名长度必须为6到18个字符', log_level=logging.WARNING)
USERNAME_WITH_ILLEGAL_CHAR = ErrorReason(
    1000, '用户名只能包含英文字母、数字、下划线', log_level=logging.WARNING)
USERNAME_ENDSWITH_ILLEGAL_CHAR = ErrorReason(
    1000, '用户名必须以字母或数字结尾', log_level=logging.WARNING)
PASSWORD_LENGTH_ERROR = ErrorReason(
    1000, '密码长度必须为6到16个字符', log_level=logging.WARNING)
PASSWORD_WITH_SPACE_HEAD_TAIL = ErrorReason(
    1000, '密码不能以空格开头或结尾', log_level=logging.WARNING)
PASSWORD_WITH_NON_ASCII = ErrorReason(
    1000, '密码中不能包含非ASCII字符', log_level=logging.WARNING)
PASSWORD_WITH_INVALID_CHAR = ErrorReason(
    1000, '密码中不能包含不可见字符', log_level=logging.WARNING)

##########################
# 业务逻辑异常
##########################
ORDER_STATUS_ERROR = ErrorReason(4000, '订单状态异常')
OBF_ID_GEN_ERROR = ErrorReason(4000, '服务器未知异常，请联系客服')
ORDER_TIMEOUT_ERROR = ErrorReason(4000, '订单已超时关闭')
ORDER_INFO_ERROR = ErrorReason(4000, '订单信息有误，请联系客服')
PARAMS_ERROR = ErrorReason(4000, '参数异常')
PAYMETHOD_DISABLED = ErrorReason(4000, '该支付方式维护中，请改用其它方式支付')
ORDER_NOT_INIT_ERROR = ErrorReason(4000, '该订单支付结果确认中，请返回重新购买')

##########################
# 系统内部错误
##########################
UNKNOWN_ERROR = ErrorReason(5000, '未知异常，请稍后重试')
SERVER_MAINTAIN_ERROR = ErrorReason(5001, '系统维护中，请稍后重试')
QRCODE_GEN_ERROR = ErrorReason(5003, '生成失败，请刷新后重试')
QRCODE_QUERY_ERROR = ErrorReason(5003, '查询二维码失败，请稍后重试')

# 数据库错误
MYSQL_OP_ERROR = ErrorReason(5002, '数据库操作失败')
SUB_MYSQL_OP_ERROR = ErrorReason(5002, '数据库操作失败')
SUB_MYSQL_UNAVAILABLE_ERROR = ErrorReason(5002, '数据库维护中')
REDIS_QUEUE_FULL_ERROR = ErrorReason(5002, '缓存队列已满')
MONGO_OP_ERROR = ErrorReason(5002, '数据库操作失败')
MYSQL_LEVEL_ERROR = ErrorReason(5003, '系统升级维护中，请稍后重试')
ORDER_ARCHIVED_ERROR = ErrorReason(5004, '订单记录已归档，无法进行此操作')


class BaseError(Exception):
    """
    异常基类，本项目代码中抛出的异常必须是他的子类
    """

    def __init__(self, reason, message, status_code=500, ext_info=None):
        """
        构建异常基类
        :param self:
        :param reason: 定义错误类别的对象，参考ErrorReason
        :param message: 描述错误的具体原因的字符串，用于记录日志，给开发人员查看
        :param status_code:
        :param ext_info:
        :return:
        """
        super(BaseError, self).__init__(message)
        self.reason = reason
        self.message = message
        self.status_code = status_code
        self.ext_info = ext_info


class BadRequestError(BaseError):
    """
    错误请求的异常类，捕捉后会抛出400
    """

    def __init__(self, reason, message, ext_info=None):
        super(BadRequestError, self).__init__(reason, message, 400, ext_info)


class ResourceNotFoundError(BaseError):
    """
    资源请求失败的异常类，捕捉后会抛出404
    """

    def __init__(self, reason, message, ext_info=None):
        super(ResourceNotFoundError, self).__init__(
            reason, message, 404, ext_info)


class InternalServerError(BaseError):
    """
    内部异常，例如数据库操作异常等，捕捉后会抛出500
    """

    def __init__(self, reason, message, ext_info=None):
        super(InternalServerError, self).__init__(
            reason, message, 500, ext_info)


class BusinessError(BaseError):
    """
    业务逻辑异常，例如URS相关异常等等，捕捉后会抛出500
    """

    def __init__(self, reason, message, ext_info=None):
        super(BusinessError, self).__init__(reason, message, 500, ext_info)


class PermissionError(BaseError):
    """
    操作权限异常，捕捉后会抛出403
    """

    def __init__(self, reason, message, ext_info=None):
        super(PermissionError, self).__init__(reason, message, 403, ext_info)


class StorageError(BaseError):
    """
    后端存储异常，捕捉后会抛出500
    """

    def __init__(self, reason, message, ext_info=None):
        super(StorageError, self).__init__(reason, message, 500, ext_info)
