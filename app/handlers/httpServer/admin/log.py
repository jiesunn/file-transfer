# coding: utf-8

from flask import (Blueprint, request, session,
                   render_template, Response,
                   )

from . import check_power
from .. import CODE
from app.lib.common import my_json_res
from app.lib.models import User, Log

admin_log = Blueprint('admin_log', __name__, url_prefix='/admin')


@admin_log.before_request
def check():
    check_power()


@admin_log.route('/log', methods=['GET'])
def index():
    params = request.args
    page = int(params.get('page')) if params.get('page') else 1
    user = User().get_by_sub(session['sub'])
    logList = Log().query_list({}, page)
    count = Log().query_list_num({})
    return render_template('admin/log.html', title='请求日志', user=user,
                           logList=logList, count=count, page=page)


@admin_log.route('/log/query', methods=['GET', 'POST'])
def query():
    params = request.args
    page = int(params.get('page')) if params.get('page') else 1
    if request.method == 'POST':
        params = request.form
        url = ('/admin/log/query?type=' + params.get('type') +
               '&content=' + params.get('content') +
               '&page=' + str(page))
        return Response(my_json_res(CODE.SUCCESS, {'url': url}, ''), content_type='application/json')
    data = {
        params.get('type'): params.get('content')
    }
    user = User().get_by_sub(session['sub'])
    logList = Log().query_list(data, page)
    count = Log().query_list_num(data)
    return render_template('admin/log.html', title='请求日志', user=user,
                           logList=logList, count=count, page=page,
                           type=params.get('type'), content=params.get('content'))

