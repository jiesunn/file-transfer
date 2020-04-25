from flask import Blueprint, render_template, session, redirect, url_for
from app import *

http = Blueprint('http', __name__)


@http.route('/login')
@http.route('/login/<open_id>')
def login(open_id=None):
    if open_id:
        session['open_id'] = open_id
        return redirect(url_for('http.home'))
    return 'login page'


@http.route('/home')
def home():
    if REDIS.hexists(USER_MAP_HOME, session['open_id']):
        return '您已打开一个home页面，请先关闭！'
    return render_template('home.html')


@http.route('/room/')
@http.route('/room/<room_id>')
def room(room_id=None):
    if room_id:
        if REDIS.hexists(ROOM_MAP, room_id):
            room_id = REDIS.hget(ROOM_MAP, room_id).decode()
            room_id_arr = room_id.split('_')
            if session['open_id'] == room_id_arr[0] or session['open_id'] == room_id_arr[1]:
                return render_template('room.html')
    return '您不属于该房间！'
