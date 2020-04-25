$(function () {
    // 兼容浏览器差异
    const PeerConnection = (window.PeerConnection || window.webkitPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection),
        IceCandidate = (window.mozRTCIceCandidate || window.RTCIceCandidate),
        SessionDescription = (window.mozRTCSessionDescription || window.RTCSessionDescription),
        URL = (window.URL || window.webkitURL),
        config = {
            "iceServers": [{
                "url": "stun:stun.l.google.com:19302"
            }]
        };
    let peerConn = [], fileChannel = [];

    // 建立ws连接
    const websocket_url = 'ws://' + document.domain + ':' + location.port + '/room',
        socket = io.connect(websocket_url),
        roomID = window.location.pathname.split('/')[2];

    // 用户信息
    let isInitiator, curOpenID, oppOpenID;

    // 文件信息
    const packetSize = 10 * 1024; // 10kb
    let sendFileList = [], receiveFileList = [];

    // WebRTC计时器
    let timerWebRTC = [],
        setWebRTCInterval = function (fileID) {
            delete peerConn[fileID];
            delete fileChannel[fileID];
            timerWebRTC[fileID] = setInterval(function () {
                createPeerConn(fileID);
            }, 5 * 1000);
        },
        clearWebRTCInterval = function (fileID) {
            clearInterval(timerWebRTC[fileID]);
        };

    socket.on('connect', function () {
        console.log('connect: ' + websocket_url);
        socket.emit('join', {'room_id': roomID});
    });

    socket.on('disconnect', function () {
        console.log('disconnect ' + websocket_url);
    });

    // 监听回复消息
    socket.on('message', function (data) {
        let code = data.code;
        switch (code) {
            case 200:
                $('#show').append('<li class="success">' + data.msg + '</li>');
                break;
            case -1:
                $('#show').append('<li class="error">' + data.msg + '</li>');
                break;
            case 101:
                isInitiator = data.data.is_initiator;
                curOpenID = data.data.cur_open_id;
                oppOpenID = data.data.opp_open_id;
                $('#sendFileBtn').removeAttr("disabled");
            case 100:
                $('#show').append('<li>' + data.msg + '</li>');
                break;
            default:
                console.log('not found');
        }
    });

    /***********************
     *       WebRTC
     ***********************/

    // 监听信令
    socket.on('signal', function (data) {
        let type = data.type,
            fileID = data.fileID,
            pc = peerConn[fileID];
        switch (type) {
            case 'offer':
                pc.setRemoteDescription(new SessionDescription(data.data), function () {
                    console.log('成功获得offer，发送answer。');
                    pc.createAnswer().then(function (answer) {
                        return pc.setLocalDescription(answer);
                    }).then(function () {
                        sendSignal('answer', pc.localDescription, fileID);
                    }).catch(function (error) {
                        logError(error)
                    });
                }).catch(function (error) {
                    logError(error)
                });
                break;
            case 'answer':
                pc.setRemoteDescription(new SessionDescription(data.data), function () {
                    console.log('成功获得answer');
                }).catch(function (error) {
                    logError(error)
                });
                break;
            case 'candidate':
                console.log('收到candidate');
                pc.addIceCandidate(new IceCandidate({
                    sdpMid: data.data.sdpMid,
                    sdpMLineIndex: data.data.sdpMLineIndex,
                    candidate: data.data.candidate,
                }));
                break;
            case 'file':
                console.log('创建fileChannel：' + fileID);
                createPeerConn(fileID);
                break;
            default:
                console.log('not found');
        }
    });

    // 创建peer连接
    function createPeerConn(fileID) {
        // 设置WebRTC定时器
        if (! peerConn.hasOwnProperty(fileID)) {
            setWebRTCInterval(fileID);
        }

        console.log('创建作为发起方的WebRTC连接？', isInitiator);
        peerConn[fileID] = new PeerConnection(config);
        let pc = peerConn[fileID];

        // 交换candidate
        pc.onicecandidate = function (event) {
            if (event.candidate) {
                sendSignal('candidate', event.candidate, fileID);
                console.log('交换candidate');
            } else {
                console.log('结束candidates交换');
            }
        };

        // 是否为发起方
        if (isInitiator) {
            // 创建文件数据通道
            fileChannel[fileID] = pc.createDataChannel(fileID);
            onFileChannelCreated(fileChannel[fileID]); // 监听数据通道

            pc.createOffer().then(function (offer) {
                return pc.setLocalDescription(offer);
            }).then(function () {
                console.log('创建一个offer并发送');
                sendSignal('offer', pc.localDescription, fileID);
            }).catch(function (error) {
                logError(error)
            });
        } else {
            pc.ondatachannel = function (event) {
                let fileID = event.channel.label;
                fileChannel[fileID] = event.channel;
                onFileChannelCreated(fileChannel[fileID]); // 监听数据通道
            };
        }
    }

    // 监听数据通道
    function onFileChannelCreated(channel) {
        // 数据通道打开
        channel.onopen = function () {
            onOpenCallback(channel.label);
        };

        // 接受数据通道的数据
        channel.onmessage = function (event) {
            onMessageCallback(event);
        };
    }

    // 发送signal
    function sendSignal(type = '', data = {}, fileID) {
        socket.emit('signal', {
            'type': type,
            'room_id': roomID,
            'opp_open_id': oppOpenID,
            'data': data,
            'fileID': fileID,
        });
    }

    // 错误日志
    function logError(err) {
        if (!err) return;
        if (typeof err === 'string') {
            console.warn(err);
        } else {
            console.warn(err.toString(), err);
        }
    }

    /***********************
     *       文件传输
     ***********************/

    // 数据通道打开
    function onOpenCallback(fileID) {
        clearWebRTCInterval(fileID); // 通道打开则移除计时器
        if (sendFileList.hasOwnProperty(fileID)) {
            sendFileDesc(fileID); // 传输文件描述包
        }
        console.log('fileChannel已打开：', fileID);
    }

    // 接收数据
    function onMessageCallback(event) {
        let fileID = event.target.label;
        if (typeof event.data == 'string') {
            let packet = JSON.parse(event.data),
                type = packet.type;
            switch (type) {
                case 'desc':
                    receiveFileDesc(fileID, packet); // 接受文件描述包
                    break;
                case 'ack':
                    sendFileChunk(fileID); // 继续发送数据
                    break;
                default:
                    console.log('not found')
            }
        } else {
            receiveFileChunk(fileID, event.data); // 接收数据包
        }
    }

    // 监听发送按钮
    $('#sendFileBtn').click(function () {
        let file = $('#fileIpt').get(0).files[0];
        if (file) {
            // 设置文件样式
            let fileID = getRandomString(),
                fileName = file.name,
                fileSize = byteConvert(file.size);
            setFileView(fileID, fileName, fileSize, true);

            // 使用FileReader读取文件
            let reader = new FileReader();
            reader.readAsArrayBuffer(file);
            reader.onload = function (event) {
                let fileData = event.target.result,
                    fileLength = fileData.byteLength;
                sendFileList[fileID] = {
                    fileName: fileName, // 文件名
                    fileSize: fileSize, // 文件大小
                    fileLength: fileLength, // 文件字节数
                    fileData: fileData, // 文件数据
                    curPackets: 0, // 当前发送的包数
                };
                sendSignal('file', {}, fileID);
                console.log(sendFileList[fileID]);
            };
        }
    });

    // 发送文件描述包
    function sendFileDesc(fileID) {
        let descPacket = {
            type: 'desc',  // 描述
            fileName: sendFileList[fileID].fileName, // 文件名
            fileSize: sendFileList[fileID].fileSize, // 文件大小
            fileLength: sendFileList[fileID].fileLength, // 文件字节数
        };
        fileChannel[fileID].send(JSON.stringify(descPacket));
        console.log(descPacket);
    }

    // 发送文件
    function sendFileChunk(fileID) {
        // 发送数据包
        let sendFile = sendFileList[fileID],
            start = sendFile.curPackets * packetSize,
            end = Math.min(sendFile.fileLength, start + packetSize),
            packet = sendFile.fileData.slice(start, end);
        fileChannel[fileID].send(packet);
        console.log(fileID, packet);

        // 设置进度
        sendFile.curPackets++;
        setProcessView(fileID, end, sendFile.fileLength);

        // 发送完则删除缓存
        if (end === sendFile.fileLength) {
            delete sendFileList[fileID];
            delete fileChannel[fileID];
            delete peerConn[fileID];
            console.log('清除发送文件缓存', fileID);
        }
    }

    // 接受文件描述
    function receiveFileDesc(fileID, packet) {
        console.log(fileID, packet);
        receiveFileList[fileID] = {
            fileName: packet.fileName, // 文件名
            fileSize: packet.fileSize, // 文件大小
            fileLength: packet.fileLength, // 文件字节数
            fileData: [], // 文件数据
            curLength: 0, // 当前接收的字节数
        };
        setFileView(fileID, packet.fileName, packet.fileSize, false);
        fileChannel[fileID].send(JSON.stringify({type: 'ack'}));
    }

    // 接收文件
    function receiveFileChunk(fileID, data) {
        // 接收数据
        let receiveFile = receiveFileList[fileID];
        receiveFile.fileData.push(data);
        receiveFile.curLength += data.byteLength;

        // 设置进度
        setProcessView(fileID, receiveFile.curLength, receiveFile.fileLength);
        if (receiveFile.curLength === receiveFile.fileLength) {
            fileChannel[fileID].send(JSON.stringify({type: 'done'}));
            downloadFile(fileID);
            console.log('下载文件', fileID);
            return;
        }

        // 发送应答包
        fileChannel[fileID].send(JSON.stringify({type: 'ack'}));
        console.log(fileID, data);
    }

    // 接收到所有文件碎片后将其组合成一个完整的文件并自动下载
    function downloadFile(fileID) {
        let receiveFile = receiveFileList[fileID],
            hyperlink = document.createElement("a"),
            mouseEvent = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
            });
        hyperlink.target = '_blank';
        hyperlink.href = URL.createObjectURL(new Blob(receiveFile.fileData));
        hyperlink.download = receiveFile.fileName;
        hyperlink.dispatchEvent(mouseEvent);
        URL.revokeObjectURL(hyperlink.href);

        // 清除接受文件缓存
        delete receiveFileList[fileID];
        delete fileChannel[fileID];
        delete peerConn[fileID];
        console.log('清除接受文件缓存', fileID);
    }

    // 获得随机字符串来生成文件ID
    function getRandomString() {
        return (Math.random() * new Date().getTime()).toString(36).toUpperCase().replace(/\./g, '-');
    }

    // 设置文件传输显示
    function setFileView(fileID, fileName, fileSize, send = true) {
        let info = send ? '发送：' : '接收：';
        info += fileName + '，大小 ' + fileSize;
        $('#show').append('<li id="file_' + fileID + '">' + info + ' 【 <span>请稍后...</span> 】</li>');
    }

    // 设置进度显示
    function setProcessView(fileID, curLength, fileLength) {
        let id = '#file_' + fileID,
            percent = curLength / fileLength * 100;
        percent = curLength === fileLength ? '完成' : percent.toFixed(2) + '%';
        $(id + ' > span').text(percent);
    }

    // 字节单位换算
    function byteConvert(bytes) {
        if (isNaN(bytes)) {
            return '';
        }

        let symbols = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            exp = Math.floor(Math.log(bytes) / Math.log(2));
        exp = exp < 1 ? 0 : exp;

        let i = Math.floor(exp / 10);
        bytes = bytes / Math.pow(2, 10 * i);
        if (bytes.toString().length > bytes.toFixed(2).toString().length) {
            bytes = bytes.toFixed(2);
        }
        return bytes + symbols[i];
    }
});