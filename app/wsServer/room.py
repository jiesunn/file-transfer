from app.wsServer import *

wsRoom = Blueprint('wsRoom', __name__)


# 建立ws连接，建立open_id与sid的映射关系
@socketIO.on('connect', namespace='/room')
def room_connect():
    REDIS.hset(USER_MAP_ROOM, session['open_id'], request.sid)


# 断开ws连接，删除open_id与sid的映射关系
@socketIO.on('disconnect', namespace='/room')
def room_disconnect():
    REDIS.hdel(USER_MAP_ROOM, session['open_id'])


# 加入房间
@socketIO.on('join', namespace='/room')
def room_join(data):
    room_id = data.get('room_id')
    cur_open_id = session['open_id']
    cur_sid = request.sid

    # 检查房间
    if not check_room(room_id, cur_open_id, cur_sid):
        return

    # 加入房间
    ROOM_SET_KEY = ROOM_SET % room_id
    REDIS.sadd(ROOM_SET_KEY, session['open_id'])
    join_room(room_id, cur_sid)
    msg = 'open_id为' + cur_open_id + '的用户加入房间！'

    # 设置双方的返回data
    opp_open_id = get_opp_open_id(room_id, cur_open_id)
    opp_sid = get_opp_sid(opp_open_id)
    cur_data = {
        'room_id': room_id,
        'cur_open_id': cur_open_id,
        'opp_open_id': opp_open_id,
        'is_initiator': True
    }
    opp_data = {
        'room_id': room_id,
        'cur_open_id': opp_open_id,
        'opp_open_id': cur_open_id,
        'is_initiator': False
    }

    # 未满房则等待，满房则删除相关缓存
    if REDIS.scard(ROOM_SET_KEY) < 2:
        msg += '等候另一位用户...'
        emit('message', my_response(100, {}, msg), room=room_id)
    else:
        REDIS.hdel(ROOM_MAP, room_id)
        REDIS.delete(ROOM_SET_KEY)
        msg += '请在下方选择文件开始传输！'
        emit('message', my_response(101, cur_data, msg), room=cur_sid)
        emit('message', my_response(101, opp_data, msg), room=opp_sid)
    return


# 转发信令
@socketIO.on('signal', namespace='/room')
def room_send_ice(signal):
    room_id = signal.get('room_id')
    opp_open_id = signal.get('opp_open_id')
    opp_sid = get_opp_sid(opp_open_id)
    signal_type = signal.get('type')
    if signal_type == 'file':
        emit('signal', signal, room=room_id)
    else:
        emit('signal', signal, room=opp_sid)


# 检查房间
def check_room(room_id, cur_open_id, cur_sid):
    # 房间不存在
    if not REDIS.hexists(ROOM_MAP, room_id):
        data = {'room_id': room_id}
        msg = '该房间不存在！'
        emit('message', my_response(-1, data, msg), room=cur_sid)
        return False

    # 没有权限
    room = REDIS.hget(ROOM_MAP, room_id).decode()
    room_id_arr = room.split('_')
    if not cur_open_id == room_id_arr[0] and not cur_open_id == room_id_arr[1]:
        data = {'room_id': room_id}
        msg = '您不属于该房间！'
        emit('message', my_response(-1, data, msg), room=cur_sid)
        return False

    return True


# 获取对面的open_id
def get_opp_open_id(room_id, cur_open_id):
    if REDIS.hexists(ROOM_MAP, room_id):
        room = REDIS.hget(ROOM_MAP, room_id).decode()
        room_id_arr = room.split('_')
        opp_open_id = room_id_arr[1] if cur_open_id == room_id_arr[0] else room_id_arr[0]
        return opp_open_id
    else:
        return ''

# 获取对面的sid
def get_opp_sid(opp_open_id):
    if REDIS.hexists(USER_MAP_ROOM, opp_open_id):
        return REDIS.hget(USER_MAP_ROOM, opp_open_id).decode()
    return ''