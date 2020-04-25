from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

from app.config import config

async_mode = None
socketIO = SocketIO()

# redis相关key
REDIS = config['development'].SESSION_REDIS
USER_MAP_HOME = 'user_map_home'
USER_MAP_ROOM = 'user_map_room'
ROOM_MAP = 'room_map'
ROOM_SET = 'room_set_%s'


# 初始化程序实例
def create_app():
    app = Flask(__name__)
    app.config.from_object(config['development'])

    socketIO.init_app(app)
    Session(app)

    # 注册蓝图
    from app.httpServer.index import http
    from app.wsServer.home import wsHome
    from app.wsServer.room import wsRoom
    app.register_blueprint(http)
    app.register_blueprint(wsHome)
    app.register_blueprint(wsRoom)

    return app
