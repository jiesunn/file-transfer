# coding: utf-8

from flask import (Blueprint, redirect, request,
                   session, url_for, render_template,
                   Response, )

from . import CODE
from app.lib.auth import auth_url, auth_req, auth_decode
from app.lib.models import User
from app.lib.common import my_json_res

login = Blueprint('login', __name__, url_prefix='/login')


@login.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    user = User().load({
        'sub': request.form.get('sub'),
        'pwd': request.form.get('pwd')
    })
    if not user.login():
        res = my_json_res(CODE.ERROR, {}, '用户名或密码错误！')
    else:
        session['sub'] = user.sub
        res = my_json_res(CODE.SUCCESS, {}, '登录成功！')
    return Response(res, content_type='application/json')


@login.route('/out', methods=['GET'])
def logout():
    del session['sub']
    return redirect(url_for('login.index'))


@login.route('/auth', methods=['GET'])
def auth():
    scope = 'openid fullname'
    url = auth_url(scope)
    if url:
        return redirect(url)
    return render_template('error.html')


@login.route('/auth/cb', methods=['GET'])
def auth_cb():
    code = request.args.get('code') or ''
    if code == '':
        msg = request.args.get('error') or 'no code'
        return render_template('error.html', msg=msg)

    res, content = auth_req(code)
    if res.getcode() != CODE.SUCCESS:
        return content.get('error')
    data = auth_decode(content)

    user = User()
    if not user.get_by_sub(data.get('sub')):
        user.create(session['sub'])
    session['sub'] = user.sub
    session['pid'] = user.pid
    return redirect(url_for('home.index'))
