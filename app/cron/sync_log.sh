#!/bin/bash

# crond
# */10 * * * * sh /usr/src/app/cron/sync_log.sh >> /usr/src/app/cron.log

# shellcheck disable=SC2164
cd /usr/src
if [ ! -f "app/cron.log" ];then
touch app/cron.log
echo "新创建log文件" > app/cron.log
fi
python -m app.cron.sync_log
