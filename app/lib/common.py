import hashlib
import json
import time


def my_md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


def my_msg(msg):
    localtime = time.strftime("%H:%M:%S", time.localtime())
    return '[' + localtime + '] ' + msg


def my_json_res(code, data, msg):
    return json.dumps({
        'code': code,
        'data': data,
        'msg': msg,
    })


def my_ws_res(code, data, msg):
    return {
        'code': code,
        'data': data,
        'msg': msg,
    }
