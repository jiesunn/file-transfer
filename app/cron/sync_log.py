# coding: utf8

"""
同步日志定时任务（）
"""

import json
from datetime import datetime, date, timedelta

from app.lib.models import Log


def main():
    log_list = Log().get_list()
    data_list = {}
    key_list = []
    for key, value in log_list.items():
        data_list[key] = json.loads(value)
        key_list.append(key)
    if Log().save_list(data_list):
        Log().del_list(key_list)
        print('已同步请求日志')
    now = datetime.now()
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
    if Log().del_date_key(yesterday):
        print('已删除', yesterday, '的log date key')
    print('执行完成', now.strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    main()
