# coding: utf-8

# 加载所有蓝图
from .httpServer.login import login
from .httpServer.user.home import home
from .httpServer.user.file import file
from .httpServer.admin.user import admin_user
from .httpServer.admin.log import admin_log
from .httpServer.admin.monitor import admin_monitor
from .wsServer.file import wsFile
