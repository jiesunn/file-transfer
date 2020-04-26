# coding: utf-8

import time

from flask import Blueprint, Response, render_template, session

from app.lib.models import User, File

file = Blueprint('file', __name__, url_prefix='/file')


@file.route('/', methods=['GET'])
def index():
    user = User().load({'sub': session['sub']})
    if user.get_ws_sid():
        return render_template('user/file-refresh.html', title="文件传输", user=user)
    return render_template('user/file.html', title="文件传输", user=user)


@file.route('/download/<file_id>')
def generate_download(file_id=''):
    fileModel = File().load({'id': file_id})
    desc = fileModel.get_desc()
    if not desc:
        return '文件不存在'
    size, filename = desc.size, desc.name.encode("utf-8").decode("latin1")

    def generate():
        cur, count = 0, 0
        while cur < size:
            # 传输数据包
            fileModel.load({'start': str(cur)})
            fileData, length = fileModel.get_data()
            if fileData and length:
                fileModel.del_data()
                cur += int(length)
                count = 0
                yield fileData
                continue

            # 暂停与中断判断
            desc_new = File().load({'id': fileModel.id}).get_desc()
            if not desc_new:
                return '文件不存在'
            if desc_new.state == 0:
                count += 1
            if desc_new.state == -1 or count >= 10:
                desc_new.state = -1
                desc_new.set_desc()
                break
            time.sleep(1)

    response = Response(generate(), content_type='application/octet-stream')
    response.headers['Content-disposition'] = 'attachment; filename=%s' % filename
    response.headers['Content-length'] = size
    return response
