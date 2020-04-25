# coding: utf-8

from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

from app.config import config, ENV

my_config = config[ENV]
async_mode = None
socketIO = SocketIO()


# 初始化程序实例
def create_app():
    app = Flask(__name__)
    app.config.from_object(my_config)

    socketIO.init_app(app)
    Session(app)

    # 注册蓝图
    from app.handlers import (login, home, file, admin_user, admin_log, admin_monitor, wsFile)
    app.register_blueprint(login)
    app.register_blueprint(home)
    app.register_blueprint(file)
    app.register_blueprint(admin_user)
    app.register_blueprint(admin_log)
    app.register_blueprint(admin_monitor)
    app.register_blueprint(wsFile)

    return app
