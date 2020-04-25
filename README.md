# 基于webRTC的p2p文件传输web应用

## 前言

### 技术要点

1. 如何基于web实现客户端至客户端的文件传输，且服务器端不保存文件
2. 如何显示传输进度
3. 如何对大文件传输进行优化
4. 如何断点续传（TODO）

### 具体实现

#### openid

> 使用openid登录（TODO）

#### Redis

> 做少量数据存储（Session、账号库、在线用户）

#### WebSocket

> 用以推送消息、交换信令

#### WebRTC

> 建立浏览器间p2p数据通道

### 协议

- message 
```
{
    code: -1 || 100 || 200 || 101,
    data: {},
    msg: '提示信息',
}
```

- signal
```
{
    type: 'offer' || 'answer' || 'candidate' || 'file',
    room_id: roomID,
    opp_open_id: oppOpenID,
    data: {},
    fileID: fileID,
}
```

- packet
```
{
    type: 'desc' || 'ack' || 'done',
    ...
}
```

## 细节

### 依赖包版本

> requirements.txt

### 环境搭建（具体看Dockerfile）

> Docker + Alpine + Flask + Gunicorn