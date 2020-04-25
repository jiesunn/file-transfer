#!/bin/bash

# chmod u+x *.sh 赋予执行权限

# 获取工作目录的绝对路径
work_path=$(cd "$(dirname "$0")"; pwd)

# 创建Redis容器（首次搭建项目 or 重新创建Redis容器）
docker stop redis
docker container rm redis
docker image rm redis:5.0.4-alpine
docker pull redis:5.0.4-alpine
docker run -d --restart=unless-stopped -p 6379:6379 \
  -v ${work_path}/redisData:/data \
  --name redis redis:5.0.4-alpine redis-server --appendonly yes
docker inspect redis | grep Gateway

# 删除应用容器与镜像
docker stop file-transfer
docker container rm file-transfer
docker image rm flask:latest

# 构建应用镜像及容器
docker build -t flask .
docker run -d -p 8000:8000 -v ${work_path}/app:/usr/src/app --name file-transfer flask