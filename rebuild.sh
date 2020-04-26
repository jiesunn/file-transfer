#!/bin/bash

# chmod u+x *.sh 赋予执行权限

# 获取工作目录的绝对路径
work_path=$(cd "$(dirname "$0")"; pwd)

# 重建Redis容器
docker stop redis
docker container rm redis
docker image rm redis:5.0.4-alpine
docker pull redis:5.0.4-alpine
docker run -d --restart=unless-stopped -p 6379:6379 \
  -v ${work_path}/redisData:/data \
  --name redis redis:5.0.4-alpine redis-server --appendonly yes
docker inspect redis | grep Gateway

# 重建MySQL容器
docker stop mysql
docker container rm mysql
docker image rm mysql:5.7
docker pull mysql:5.7
docker run -p 3307:3306 --name mysql \
  -v ${work_path}/mysql/conf:/etc/mysql \
  -v ${work_path}/mysql/logs:/var/log/mysql \
  -v ${work_path}/mysql/data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=file-transfer \
  -d mysql:5.7

# 重建应用容器
docker stop file-transfer
docker container rm file-transfer
docker image rm flask:latest
docker build -t flask .
docker run -d -p 8000:8000 \
  -v ${work_path}/app:/usr/src/app \
  -v ${work_path}/log:/usr/src/log \
  --name file-transfer flask