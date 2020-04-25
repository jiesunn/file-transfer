# coding: utf-8

from flask import session, render_template

from app.lib.models import User, power


def check_power():
    user = User().get_by_sub(session['sub'])
    if user.pid is not power.ADMIN:
        return render_template('user/no-power.html', title='权限不足', user=user)
