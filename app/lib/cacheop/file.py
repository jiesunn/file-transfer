# coding: utf-8

from . import Redis

_REDIS = Redis().POOL

_FILE_DESC = 'FILEDESC_%s'
_FILE_DATA = 'FILEDATA_%s_%s'
_FILE_LEN = 'FILELEN_%s_%s'
_FILE_DESC_EX = 10 * 3600
_FILE_DATA_EX = 10


def get_file_desc(file_id=None):
    if file_id is None:
        return False
    return _REDIS.get(_FILE_DESC % file_id)


def get_file_desc_list():
    key_list = _REDIS.keys(_FILE_DESC % '*')
    desc_list = []
    for key in key_list:
        desc_list.append(_REDIS.get(key))
    return desc_list


def set_file_desc(file_id=None, desc=None):
    if file_id is None or desc is None:
        return False
    return _REDIS.set(_FILE_DESC % file_id, desc, ex=_FILE_DESC_EX)


def del_file_desc(file_id=None):
    if file_id is None:
        return False
    return _REDIS.delete(_FILE_DESC % file_id)


def get_file_data(file_id=None, start=None):
    redis = Redis(decode=False).POOL
    if file_id is None or start is None:
        return False, False
    return (redis.get(_FILE_DATA % (file_id, start)),
            _REDIS.get(_FILE_LEN % (file_id, start)))


def set_file_data(file_id=None, start=None, data=None, length=None):
    if file_id is None or start is None or data is None or length is None:
        return False
    _REDIS.set(_FILE_DATA % (file_id, start), data, ex=_FILE_DATA_EX)
    _REDIS.set(_FILE_LEN % (file_id, start), length, ex=_FILE_DATA_EX)
    return True


def del_file_data(file_id=None, start=None):
    if file_id is None:
        return False
    _REDIS.delete(_FILE_DATA % (file_id, start))
    _REDIS.delete(_FILE_LEN % (file_id, start))
    return True
