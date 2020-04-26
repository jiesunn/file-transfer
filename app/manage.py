import logging
import json
import sys
from datetime import datetime

sys.path.append(r"/usr/src")

from flask import session, redirect, url_for, request
from app import create_app
from app.lib.models import Log

app = create_app()


@app.before_request
def print_request_info():
    prefix = request.full_path.split('/')
    if len(prefix) >= 2:
        if prefix[1] == 'static':
            return
        if prefix[1] != 'login':
            if 'sub' not in session:
                return redirect(url_for('login.index'))


@app.after_request
def after_app_request(response):
    path = request.full_path
    prefix = path.split('/')
    if len(prefix) >= 2:
        if prefix[1] == 'static':
            return response

    level = 'SUCCESS'
    code = response.status_code
    res = response.json if response.json else {}
    if str(code).startswith('4') or str(code).startswith('5'):
        level = 'ERROR'
    log = Log().load({
        'level': level,
        'code': code,
        'method': request.method,
        'path': path,
        'params': json.dumps(request.form),
        'response': json.dumps(res),
        'user_ip': request.remote_addr,
        'request_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    log.set()
    return response


@app.route('/')
def index():
    if 'sub' not in session:
        return redirect(url_for('login.index'))
    else:
        return redirect(url_for('home.index'))


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)
