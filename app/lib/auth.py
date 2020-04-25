# coding: utf-8

"""
open_id 认证
"""

import jwt
import json

from urllib import parse, request

from app.lib import errors

url = 'https://login.netease.com/connect'
redirect_uri = 'http://dev.file-transfer.com:8000/login/auth/cb'
client_id = '014b3cba6d7711eab83e246e965dfd84'
client_secret = 'dc842ef711ce43db8098470388836e46014b416a6d7711eab83e246e965dfd84'


def auth_url(scope):
    if not scope:
        return False
    scope = 'openid fullname'
    url_new = (url + '/authorize?response_type=code&scope=' + scope +
               '&client_id=' + client_id + '&redirect_uri=' + redirect_uri)
    return url_new


def auth_req(code):
    if not code:
        raise errors.InternalServerError(
            errors.PARAMS_ERROR,
            'code is empty')
    postDict = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    data = bytes(parse.urlencode(postDict), encoding='utf-8')
    req = request.Request(url=url + '/token', data=data, method='POST')
    res = request.urlopen(req)
    content = json.loads(res.read().decode('utf-8'))
    return res, content


def auth_decode(content):
    try:
        id_token = content.get('id_token')
        data = jwt.decode(id_token, client_secret, algorithms='HS256', issure=url, audience=client_id)
    except Exception as e:
        raise errors.InternalServerError(
            errors.PARAMS_ERROR,
            'jwt decode error')
    return data
