# coding: utf-8

from flask import (Blueprint, request, session,
                   render_template, Response, )

from .. import CODE
from app.lib.common import my_json_res
from app.lib.models import User

home = Blueprint('home', __name__, url_prefix='/home')


@home.route('/', methods=['GET'])
def index():
    userModel = User().get_by_sub(session['sub'])
    return render_template('user/home.html', title='个人主页', user=userModel)


@home.route('/profile', methods=['POST'])
def profile():
    data = {
        'sub': session['sub'],
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
        'intro': request.form.get('intro'),
    }
    userModel = User().load(data)
    res, msg = userModel.check_arrt()
    if not res:
        res = my_json_res(CODE.ERROR, {}, msg)
    else:
        userModel.update_profile()
        res = my_json_res(CODE.SUCCESS, {}, '更改个人信息成功')
    return Response(res, content_type='application/json')


@home.route('/pwd', methods=['POST'])
def pwd():
    data = {
        'sub': session['sub'],
        'pwd': request.form.get('old_pwd'),
    }
    userModel = User().load(data)
    new_pwd = request.form.get('new_pwd')
    re_pwd = request.form.get('re_pwd')
    if re_pwd != new_pwd:
        res = my_json_res(CODE.ERROR, {}, '两次密码输入不一致')
        return Response(res, content_type='application/json')
    if not userModel.reset_pwd(new_pwd):
        res = my_json_res(CODE.ERROR, {}, '输入的原密码不正确')
    else:
        del session['sub']
        res = my_json_res(CODE.SUCCESS, {}, '更新密码成功，请重新登录')
    return Response(res, content_type='application/json')
