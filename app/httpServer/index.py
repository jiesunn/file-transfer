import json, time, jwt, urllib.request, urllib.parse

from flask import Blueprint, Response, render_template
from flask import session, redirect, url_for, request

from app import *

http = Blueprint('http', __name__)


@http.route('/')
@http.route('/login')
@http.route('/login/<cb>')
def login(cb=None):
    url = 'https://login.netease.com/connect'
    redirect_uri = 'http://10.249.129.247:8000/login/cb'
    client_id = '353b762a673211eabf44246e965dfd84'
    client_secret = 'f9b7dfddaff54a70bf0ac07c8d623a2a353b7b02673211eabf44246e965dfd84'
    if cb is None:
        scope = 'openid fullname'
        url_n = url + '/authorize?response_type=code&scope=' + scope + '&client_id=' + client_id + '&redirect_uri=' + redirect_uri
        return redirect(url_n)

    code = request.args.get('code') or ''
    if code == '':
        msg = request.args.get('error') or 'no code'
        return msg
    postDict = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    data = bytes(urllib.parse.urlencode(postDict), encoding='utf-8')
    req = urllib.request.Request(url=url + '/token', data=data, method='POST')
    res = urllib.request.urlopen(req)
    content = json.loads(res.read().decode('utf-8'))

    if res.getcode() is 200:
        try:
            id_token = content.get('id_token')
            data = jwt.decode(id_token, client_secret, algorithms='HS256', issure=url, audience=client_id)
        except Exception as e:
            return e
        session['sub'] = data.get('sub')
        return redirect(url_for('http.home'))
    return content.get('error')


@http.route('/home')
@http.route('/home/<sub>')
def home(sub=None):
    if session['sub'] is None:
        return redirect(url_for('http.login'))
    if sub is None:
        return redirect('/home/' + session['sub'])
    if sub != session['sub']:
        return redirect('/home/' + session['sub'])
    if REDIS.hexists(USER_MAP, session['sub']):
        return render_template('refresh.html')
    return render_template('home.html')


@http.route('/download/<file_id>')
def generate_download(file_id=''):
    FILE_DESC_KEY = FILE_DESC % file_id
    if not REDIS.exists(FILE_DESC_KEY):
        return '文件不存在'
    desc = json.loads(REDIS.get(FILE_DESC_KEY).decode())
    size, filename = desc.get('size'), desc.get('name').encode("utf-8").decode("latin1")

    def generate():
        cur, count = 0, 0
        while cur < size:
            # 传输数据包
            FILE_DATA_KEY = FILE_DATA % (file_id, str(cur))
            FILE_LEN_KEY = FILE_LEN % (file_id, str(cur))
            if REDIS.exists(FILE_DATA_KEY) and REDIS.exists(FILE_LEN_KEY):
                length = REDIS.get(FILE_LEN_KEY).decode()
                fileData = REDIS.get(FILE_DATA_KEY)
                REDIS.delete(FILE_LEN_KEY, FILE_DATA_KEY)
                cur += int(length)
                count = 0
                yield fileData
                continue

            # 暂停与中断判断
            if not REDIS.exists(FILE_DESC_KEY):
                return '文件不存在'
            desc_new = json.loads(REDIS.get(FILE_DESC_KEY).decode())
            if desc_new['state'] == 0: count += 1
            if desc_new['state'] == -1 or count >= 100:
                desc_new['state'] = -1
                REDIS.set(FILE_DESC_KEY, json.dumps(desc_new), FILE_DESC_EX)
                break
            time.sleep(0.1)

    response = Response(generate(), content_type='application/octet-stream')
    response.headers['Content-disposition'] = 'attachment; filename=%s' % filename
    response.headers['Content-length'] = size
    return response
