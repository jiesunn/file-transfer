#!/bin/bash

# chmod u+x *.sh 赋予执行权限

# 删除Redis
docker stop redis
docker container rm redis
docker image rm redis:5.0.4-alpine

# 删除MySQL
docker stop mysql
docker container rm mysql
docker image rm mysql:5.7

# 删除应用
docker stop file-transfer
docker container rm file-transfer
docker image rm flask:latest
