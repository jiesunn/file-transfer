# 基础镜像
FROM python:3.7.4-alpine
LABEL maintainer="lilijie@corp.netease.com"

# 创建所需目录
RUN mkdir -p /usr/src/app  && \
    mkdir -p /var/log/gunicorn

# 工作路径
WORKDIR /usr/src/app
COPY app/requirements.txt /usr/src/app/requirements.txt

# 系统依赖
RUN apk add --no-cache tzdata && \
    apk add --no-cache ca-certificates && \
    apk add --no-cache --virtual .build-deps gcc musl-dev

# python包
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /usr/src/app/requirements.txt

# 安装完成后清理缓存
RUN apk del .build-deps gcc musl-dev && \
    rm -rf /var/cache/apk/* && \
    rm -rf /usr/src/app/requirements.txt

# 设置时区
ENV TZ Asia/Shanghai

# 改为文件映射
# 复制项目至docker
# COPY ./app /usr/src/app

# 暴露端口
ENV PORT 8000
EXPOSE 8000 5000

# 启动命令
CMD ["/usr/local/bin/gunicorn", "-c", "gunicorn.conf", "manage:app"]
