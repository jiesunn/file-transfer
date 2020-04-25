# coding: utf-8

from flask import (Blueprint, request, session,
                   render_template, Response,
                   )

from . import check_power
from .. import CODE
from app.lib.common import my_json_res
from app.lib.models import User

admin_user = Blueprint('admin_user', __name__, url_prefix='/admin')


@admin_user.before_request
def check():
    check_power()


@admin_user.route('/', methods=['GET'])
@admin_user.route('/user', methods=['GET'])
def index():
    params = request.args
    page = int(params.get('page')) if params.get('page') else 1
    user = User().get_by_sub(session['sub'])
    userList = User().get_list({}, page)
    count = User().get_list_num({})
    return render_template('admin/user.html', title='用户管理', user=user,
                           userList=userList, count=count, page=page)


@admin_user.route('/user/query', methods=['GET', 'POST'])
def query():
    params = request.args
    page = int(params.get('page')) if params.get('page') else 1
    if request.method == 'POST':
        params = request.form
        url = ('/admin/user/query?type=' + params.get('type') +
               '&content=' + params.get('content') +
               '&page=' + str(page))
        return Response(my_json_res(CODE.SUCCESS, {'url': url}, ''), content_type='application/json')
    data = {
        params.get('type'): params.get('content')
    }
    user = User().get_by_sub(session['sub'])
    userList = User().get_list(data, page)
    count = User().get_list_num(data)
    return render_template('admin/user.html', title='用户管理', user=user,
                           userList=userList, count=count, page=page,
                           type=params.get('type'), content=params.get('content'))


@admin_user.route('/user/pid', methods=['POST'])
def change_pid():
    data = {
        'sub': request.form.get('sub'),
        'pid': request.form.get('pid'),
    }
    user = User().load(data)
    res = my_json_res(CODE.SUCCESS, {}, '更改权限成功')
    if not user.change_power():
        res = my_json_res(CODE.ERROR, {}, '更改权限失败')
    return Response(res, content_type='application/json')


@admin_user.route('/user/profile', methods=['POST'])
def update_profile():
    data = {
        'sub': request.form.get('sub'),
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
    }
    user = User().load(data)
    res, msg = user.check_arrt()
    if not res:
        return Response(my_json_res(CODE.ERROR, {}, msg), content_type='application/json')
    if not user.update_profile():
        return Response(my_json_res(CODE.ERROR, {}, '更改信息失败'), content_type='application/json')
    return Response(my_json_res(CODE.SUCCESS, {}, '更改信息成功'), content_type='application/json')
