# coding: utf-8

from flask import Blueprint, session, render_template, Response

from . import check_power
from .. import CODE
from app.lib.models import User, File
from app.lib.common import my_json_res

admin_monitor = Blueprint('admin_monitor', __name__, url_prefix='/admin')


@admin_monitor.before_request
def check():
    check_power()


@admin_monitor.route('/monitor', methods=['GET'])
def index():
    user = User().get_by_sub(session['sub'])
    return render_template('admin/monitor.html', title='传输监控', user=user)


@admin_monitor.route('/monitor/query', methods=['POST'])
def query():
    file_desc_list = File().get_desc_list()
    if not file_desc_list:
        return Response(my_json_res(CODE.ERROR, {}, ''), content_type='application/json')
    return Response(my_json_res(CODE.SUCCESS, file_desc_list, ''), content_type='application/json')
