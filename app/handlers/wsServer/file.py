# coding: utf-8

import json

from flask import Blueprint, session, request
from flask_socketio import emit

from . import CODE, STATE
from app import socketIO
from app.lib.models import User, File
from app.lib.common import my_ws_res

wsFile = Blueprint('wsFile', __name__, url_prefix='/wsFile')


# 建立ws连接，建立sub与sid的映射关系
@socketIO.on('connect', namespace='/wsFile')
def home_connect():
    user = User().load({'sub': session['sub']})
    user.set_ws_sid(request.sid)
    emit('connect_res', my_ws_res(CODE.SUCCESS, {'sub': session['sub']}, ''))


# 断开ws连接，删除sub与sid的映射关系
@socketIO.on('disconnect', namespace='/wsFile')
def home_disconnect():
    user = User().load({'sub': session['sub']})
    user.del_ws_sid()


# 文件描述包
@socketIO.on('file_desc', namespace='/wsFile')
def file_desc(data):
    file = File().load({
        'id': data.get('id'),
        'receiver': data.get('receiver'),
        'desc': json.dumps(data)
    })

    # 校验用户在线
    user = User().load({'sub': file.receiver})
    receiver_sid = user.get_ws_sid()
    if not receiver_sid:
        msg = '用户不在线'
        emit('sender_res', my_ws_res(CODE.ERROR, {'id': file.id}, msg))
        return

    file.set_desc()
    emit('sender_res', my_ws_res(CODE.STAY_BY, data, '等待回应...'))
    emit('receiver_res', my_ws_res(CODE.STAY_BY, data, ''), room=receiver_sid)


# 文件描述包回应
@socketIO.on('file_desc_res', namespace='/wsFile')
def file_desc_res(data):
    file = File().load({'id': data.get('file_id')})
    res = check_file_desc(file)
    if not res:
        return

    # 是否接受邀请
    if data.get('accept'):
        data = {'id': file.id, 'start': 0, 'length': 0}
        msg = ('<button class="fileDataRes accept" id="pause_' + file.id + '">暂停</button>'
               '<button class="fileDataRes refuse" id="cancel_' + file.id + '">取消</button>')
        emit('sender_res', my_ws_res(CODE.BEING, data, msg), room=res['sender_sid'])
        emit('receiver_res', my_ws_res(CODE.BEING, data, msg), room=res['receiver_sid'])
    else:
        data = {'id': file.id, 'res': res}
        emit('sender_res', my_ws_res(CODE.ERROR, data, '对方拒绝接收'), room=res['sender_sid'])
        emit('receiver_res', my_ws_res(CODE.ERROR, data, '已拒绝接收'), room=res['receiver_sid'])


# 文件数据包
@socketIO.on('file_data', namespace='/wsFile')
def file_data(data):
    # 解包并保存
    file = File()
    file.unpack(data)
    res = check_file_desc(file)
    if not res:
        return

    # 保存
    file.set_data()
    data = {
        'id': file.id,
        'start': int(file.start) + int(file.length),
        'length': file.length
    }
    res = check_file_desc(file)
    if not res:
        return
    if file.state is STATE.NORMAL:
        emit('sender_res', my_ws_res(CODE.BEING, data, ''), room=res['sender_sid'])
        emit('receiver_res', my_ws_res(CODE.BEING, data, ''), room=res['receiver_sid'])
    else:
        emit('sender_res', my_ws_res(CODE.PAUSE, data, ''), room=res['sender_sid'])
        emit('receiver_res', my_ws_res(CODE.PAUSE, data, ''), room=res['receiver_sid'])


# 文件数据操作回应包
@socketIO.on('file_data_res', namespace='/wsFile')
def file_data_res(data):
    operate = data.get('operate')
    file = File().load({
        'id': data.get('file_id'),
        'start': data.get('start')
    })
    res = check_file_desc(file)
    if not res:
        return

    code, file.state, msg = STATE.INTERRUPT, CODE.ERROR, '传输中断'
    data = {'id': file.id, 'start': file.start, 'length': 0}
    if operate == 'cancel':
        code, file.state = CODE.ERROR, STATE.INTERRUPT
        msg = '传输中断'
    elif operate == 'pause':
        code, file.state = CODE.PAUSE, STATE.PAUSE
        msg = ('<button class="fileDataRes accept" id="continue_' + file.id + '">继续</button>'
               '<button class="fileDataRes refuse" id="cancel_' + file.id + '">取消</button>')
    elif operate == 'continue':
        code, file.state = CODE.BEING, STATE.NORMAL
        msg = ('<button class="fileDataRes accept" id="pause_' + file.id + '">暂停</button>'
               '<button class="fileDataRes refuse" id="cancel_' + file.id + '">取消</button>')

    # 保存更新
    file.set_desc()
    emit('sender_res', my_ws_res(code, data, msg), room=res['sender_sid'])
    emit('receiver_res', my_ws_res(code, data, msg), room=res['receiver_sid'])


# 文件完成包
@socketIO.on('file_complete', namespace='/wsFile')
def file_complete(data):
    file = File().load({'id': data.get('file_id')})
    res = check_file_desc(file)
    if not res:
        return

    file.del_desc()
    emit('sender_res', my_ws_res(CODE.SUCCESS, {'id': file.id}, '传输完成'), room=res['sender_sid'])
    emit('receiver_res', my_ws_res(CODE.SUCCESS, {'id': file.id}, '传输完成'), room=res['receiver_sid'])


# 检查
def check_file_desc(file):
    res = {
        'sender_sid': '',
        'receiver_sid': '',
        'msg': '',
    }

    if not file.get_desc():
        res['msg'] = '文件描述包不存在'
        emit('sender_res', my_ws_res(CODE.ERROR, {'id': file.id}, res['msg']))
        emit('receiver_res', my_ws_res(CODE.ERROR, {'id': file.id}, res['msg']))
    else:
        state, sender, receiver = file.state, file.sender, file.receiver
        sid = User().load({'sub': sender}).get_ws_sid()
        if sid:
            res['sender_sid'] = sid
        else:
            res['msg'] = '发送方不存在'
        sid = User().load({'sub': receiver}).get_ws_sid()
        if sid:
            res['receiver_sid'] = sid
        else:
            res['msg'] = '接收方不存在'
        if file.state is STATE.INTERRUPT:
            res['msg'] = '传输中断'

    if len(res['msg']) > 0:
        emit('sender_res', my_ws_res(CODE.ERROR, {'id': file.id}, res['msg']), room=res['sender_sid'])
        emit('receiver_res', my_ws_res(CODE.ERROR, {'id': file.id}, res['msg']), room=res['receiver_sid'])
        file.del_desc()
        return False

    return res
