#!/bin/bash

# chmod u+x *.sh 赋予执行权限

# 停止容器
docker stop simpleFiler

# 删除容器
docker container rm simpleFiler

# 删除镜像
docker image rm flask:latest

# 构建镜像
docker build -t flask .

# 构建容器
docker run -d -p 8000:8000 -v /Users/lilijie/code/simpleFiler/app:/usr/src/app --name simpleFiler flask

# 创建Redis容器（第一次build时运行即可，rebuild不再运行）
# docker pull redis:5.0.4-alpine
# docker run -d --restart=unless-stopped -p 6379:6379 \
#    -v /Users/lilijie/code/simpleFiler/redisData:/data \
#    --name redis redis:5.0.4-alpine redis-server --appendonly yes
# docker inspect redis | grep Gateway