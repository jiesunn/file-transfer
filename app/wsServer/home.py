from app.wsServer import *

wsHome = Blueprint('wsHome', __name__)


# 建立ws连接，建立open_id与sid的映射关系
@socketIO.on('connect', namespace='/home')
def home_connect():
    REDIS.hset(USER_MAP_HOME, session['open_id'], request.sid)


# 断开ws连接，删除open_id与sid的映射关系
@socketIO.on('disconnect', namespace='/home')
def home_disconnect():
    REDIS.hdel(USER_MAP_HOME, session['open_id'])


# 邀请
@socketIO.on('invite', namespace='/home')
def home_invite(data):
    # 双方的open_id
    opp_open_id = data.get('open_id')
    cur_open_id = session['open_id']

    # 双方的返回data
    cur_data = {
        'cur_open_id': cur_open_id,
        'opp_open_id': opp_open_id
    }
    opp_data = {
        'cur_open_id': opp_open_id,
        'opp_open_id': cur_open_id
    }

    # 发起邀请方
    cur_sid = request.sid
    msg = '已向open_id为' + cur_data['opp_open_id'] + '的用户发起文件传输邀请，请稍后...'
    emit('invite_response', my_response(100, cur_data, msg), room=cur_sid)

    # 回应邀请方是否在线
    if not REDIS.hexists(USER_MAP_HOME, opp_open_id):
        # 发起邀请方
        msg = 'open_id为' + cur_data['opp_open_id'] + '的用户不存在或未上线！'
        emit('invite_response', my_response(-1, cur_data, msg), room=cur_sid)
        return

    # 回应邀请方
    opp_sid = REDIS.hget(USER_MAP_HOME, opp_open_id).decode()
    msg = 'open_id为' + opp_data['opp_open_id'] + '的用户向您发起文件传输邀请' + \
          '<button class="response" id="accept_' + opp_data['opp_open_id'] + '">接受</button>' + \
          '<button class="response" id="refuse_' + opp_data['opp_open_id'] + '">拒绝</button>'
    emit('invite_response', my_response(100, opp_data, msg), room=opp_sid)


# 邀请回应
@socketIO.on('invite_response', namespace='/home')
def home_invite_response(data):
    # 双方的open_id
    opp_open_id = data.get('open_id')
    cur_open_id = session['open_id']

    # 双方的返回数据
    cur_data = {
        'cur_open_id': cur_open_id,
        'opp_open_id': opp_open_id
    }
    opp_data = {
        'cur_open_id': opp_open_id,
        'opp_open_id': cur_open_id
    }

    # 发起邀请方不在线
    cur_sid = request.sid
    if not REDIS.hexists(USER_MAP_HOME, opp_open_id):
        msg = 'open_id为' + cur_data['opp_open_id'] + '的用户不存在或未上线！'
        emit('invite_response', my_response(-1, cur_data, msg), room=cur_sid)
        return

    # 是否接受邀请
    opp_sid = REDIS.hget(USER_MAP_HOME, opp_open_id).decode()
    if data.get('accept'):
        # 生成房间号并保存
        room_id = opp_open_id + '_' + cur_open_id
        md5_room_id = my_md5(room_id)
        REDIS.hset(ROOM_MAP, md5_room_id, room_id)
        url = '<a target="_blank" href="/room/' + md5_room_id + '">进入房间</a>'

        # 发起邀请方
        msg = 'open_id为' + opp_data['opp_open_id'] + '的用户接受了你的邀请！' + url
        emit('invite_response', my_response(200, opp_data, msg), room=opp_sid)

        # 回应邀请方
        msg = '你接受了open_id为' + cur_data['opp_open_id'] + '的用户的邀请！' + url
        emit('invite_response', my_response(200, cur_data, msg), room=cur_sid)
    else:
        # 发起邀请方
        msg = 'open_id为' + opp_data['opp_open_id'] + '的用户拒绝了你的邀请！'
        emit('invite_response', my_response(-1, opp_data, msg), room=opp_sid)

        # 回应邀请方
        msg = '你拒绝了open_id为' + cur_data['opp_open_id'] + '的用户的邀请！'
        emit('invite_response', my_response(-1, cur_data, msg), room=cur_sid)
