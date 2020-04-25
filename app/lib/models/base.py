# coding: utf-8

from .. import errors


class Base(object):
    """
    基类，提供一些基础方法
    """
    def load(self, kwargs):
        """
        批量设置属性
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def to_dict(self, *fields, **kwargs):
        """
        把属性打包为dict对象，用于输出
        """
        ret = {x: getattr(self, x) for x in fields
               if hasattr(self, x) and getattr(self, x) is not None}
        if kwargs.get('for_output'):
            if 'id' in ret:
                ret['id'] = self.obf_id()
        return ret

    def obf_id(self, *_args, **_kwargs):
        raise errors.InternalServerError(errors.UNKNOWN_ERROR, 'not implement')

