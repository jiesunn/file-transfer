import hashlib, time

def my_md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()

def my_msg(msg):
    localtime = time.strftime("%H:%M:%S", time.localtime())
    return '[' + localtime + '] ' + msg

def my_response(code, data, msg):
    return {
        'code': code,
        'data': data,
        'msg': msg,
    }
