from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

from app.config import config

async_mode = None
socketIO = SocketIO()

# redis相关key
REDIS = config['development'].SESSION_REDIS
USER_MAP = 'user_map'
FILE_DESC = 'file_desc_%s'
FILE_DATA = 'file_data_%s_%s'
FILE_LEN = 'file_len_%s_%s'
FILE_DESC_EX = 10 * 3600
FILE_DATA_EX = 10


# 初始化程序实例
def create_app():
    app = Flask(__name__)
    app.config.from_object(config['development'])

    socketIO.init_app(app)
    Session(app)

    # 注册蓝图
    from app.httpServer.index import http
    from app.wsServer.home import wsHome
    app.register_blueprint(http)
    app.register_blueprint(wsHome)

    return app
