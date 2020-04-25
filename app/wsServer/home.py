import struct

from app.wsServer import *
import json

wsHome = Blueprint('wsHome', __name__)


# 建立ws连接，建立sub与sid的映射关系
@socketIO.on('connect', namespace='/home')
def home_connect():
    REDIS.hset(USER_MAP, session['sub'], request.sid)
    emit('connect_res', my_response(200, {'sub': session['sub']}, ''))


# 断开ws连接，删除sub与sid的映射关系
@socketIO.on('disconnect', namespace='/home')
def home_disconnect():
    REDIS.hdel(USER_MAP, session['sub'])


# 文件描述包
@socketIO.on('file_desc', namespace='/home')
def file_desc(data):
    file_id = data.get('id')
    receiver = data.get('receiver')
    if not REDIS.hexists(USER_MAP, receiver):
        msg = '用户不存在'
        emit('sender_res', my_response(-1, {'id': file_id}, msg))
        return

    # 保存
    desc = json.dumps(data)
    REDIS.set(FILE_DESC % file_id, desc, FILE_DESC_EX)
    receiver_sid = REDIS.hget(USER_MAP, receiver).decode()
    emit('sender_res', my_response(0, data, '等待回应...'))
    emit('receiver_res', my_response(0, data, ''), room=receiver_sid)


# 文件描述包回应
@socketIO.on('file_desc_res', namespace='/home')
def file_desc_res(data):
    file_id = data.get('file_id')
    res = check_file_desc(file_id)
    if not res: return

    # 是否接受邀请
    if data.get('accept'):
        data = {'id': file_id, 'start': 0, 'length': 0}
        msg = '<button class="fileDataRes" id="pause_' + file_id + '">暂停</button>' \
                '<button class="fileDataRes" id="cancel_' + file_id + '">取消</button>'
        emit('sender_res', my_response(100, data, msg), room=res['sender_sid'])
        emit('receiver_res', my_response(100, data, msg), room=res['receiver_sid'])
    else:
        data = {'id': file_id, 'res': res}
        emit('sender_res', my_response(-1, data, '对方拒绝接收'), room=res['sender_sid'])
        emit('receiver_res', my_response(-1, data, '已拒绝接收'), room=res['receiver_sid'])


# 文件数据包
@socketIO.on('file_data', namespace='/home')
def file_data(data):
    file_id, start, length = '', '', ''

    # 循环3次，分别取 fileID start length
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
        if i is 0: file_id = string
        elif i is 1: start = string
        elif i is 2: length = string

    # 校验
    res = check_file_desc(file_id)
    if not res: return

    # redis存储
    fileData = data[process_len:]
    REDIS.set(FILE_DATA % (file_id, start), fileData, FILE_DATA_EX)
    REDIS.set(FILE_LEN % (file_id, start), length, FILE_DATA_EX)

    # 回应包
    data = {'id': file_id, 'start': int(start) + int(length), 'length': length}
    if res.get('desc')['state'] is 0:
        emit('sender_res', my_response(100, data, ''), room=res['sender_sid'])
        emit('receiver_res', my_response(100, data, ''), room=res['receiver_sid'])
    else:
        emit('sender_res', my_response(101, data, ''), room=res['sender_sid'])
        emit('receiver_res', my_response(101, data, ''), room=res['receiver_sid'])


# 文件数据操作回应包
@socketIO.on('file_data_res', namespace='/home')
def file_data_res(data):
    operate = data.get('operate')
    file_id = data.get('file_id')
    start = data.get('start')
    res = check_file_desc(file_id)
    if not res: return

    desc = res.get('desc')
    desc['state'], code, msg = -1, -1, '传输中断'
    data = {'id': file_id, 'start': start}
    if operate == 'cancel':
        code, desc['state'] = -1, -1
        msg = '传输中断'
    elif operate == 'pause':
        code, desc['state'] = 101, 1
        msg = '<button class="fileDataRes" id="continue_' + file_id + '">继续</button>' \
                '<button class="fileDataRes" id="cancel_' + file_id + '">取消</button>'
    elif operate == 'continue':
        code, desc['state'] = 100, 0
        msg = '<button class="fileDataRes" id="pause_' + file_id + '">暂停</button>' \
                '<button class="fileDataRes" id="cancel_' + file_id + '">取消</button>'
    desc = json.dumps(desc)
    REDIS.set(FILE_DESC % file_id, desc, FILE_DESC_EX)
    emit('sender_res', my_response(code, data, msg), room=res['sender_sid'])
    emit('receiver_res', my_response(code, data, msg), room=res['receiver_sid'])


# 文件完成包
@socketIO.on('file_complete', namespace='/home')
def file_complete(data):
    file_id = data.get('file_id')
    res = check_file_desc(file_id)
    if not res: return

    REDIS.delete(FILE_DESC % file_id)
    emit('sender_res', my_response(200, {'id': file_id}, '传输完成'), room=res['sender_sid'])
    emit('receiver_res', my_response(200, {'id': file_id}, '传输完成'), room=res['receiver_sid'])


# 检查
def check_file_desc(file_id):
    res = {
        'desc': {},
        'sender_sid': '',
        'receiver_sid': '',
        'msg': '',
    }

    FILE_DESC_KEY = FILE_DESC % file_id
    if not REDIS.exists(FILE_DESC_KEY):
        res['msg'] = '文件描述包不存在'
        emit('sender_res', my_response(-1, {'id': file_id}, res['msg']))
        emit('receiver_res', my_response(-1, {'id': file_id}, res['msg']))
    else:
        desc = json.loads(REDIS.get(FILE_DESC_KEY).decode())
        res['desc'] = desc
        state, sender, receiver = desc.get('state'), desc.get('sender'), desc.get('receiver')
        if REDIS.hexists(USER_MAP, sender):
            res['sender_sid'] = REDIS.hget(USER_MAP, sender).decode()
        else:
            res['msg'] = '发送方不存在'
        if REDIS.hexists(USER_MAP, receiver):
            res['receiver_sid'] = REDIS.hget(USER_MAP, receiver).decode()
        else:
            res['msg'] = '接收方不存在'
        if desc.get('state') is -1:
            res['msg'] = '传输中断'

    if len(res['msg']) > 0:
        emit('sender_res', my_response(-1, {'id': file_id}, res['msg']), room=res['sender_sid'])
        emit('receiver_res', my_response(-1, {'id': file_id}, res['msg']), room=res['receiver_sid'])
        REDIS.delete(FILE_DESC_KEY)
        return False

    return res