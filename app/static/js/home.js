$(function () {
    // 建立ws连接
    const websocket_url = 'ws://' + document.domain + ':' + location.port + '/home',
        socket = io.connect(websocket_url);
    let SUB;

    // 文件传输
    const sizeTimeout = 1000, transTimeout = 10 * 1000;
    const minSize = 100 * 1024, maxSize = 5 * 1024 * 1024;
    let readerList = [], sendFileList = [], receiveFileList = [];

    // 发送包大小计时器
    let sizeTimer = [], sizeCount = [],
        setSizeTimer = function (fileID) {
            let sendFile = sendFileList[fileID];
            sizeCount[fileID] = 0;
            sizeTimer[fileID] = setInterval(function () {
                sizeCount[fileID]++;
                let packetSize = sendFile.curSize - minSize;
                sendFile.curSize = packetSize < minSize ? minSize : packetSize;
                console.log(fileID + " reduce: " + sendFile.curSize);
            }, sizeTimeout);
        },
        clearSizeTimer = function (fileID) {
            delete sizeCount[fileID];
            clearInterval(sizeTimer[fileID]);
        },
        controlSize = function (fileID) {
            let sendFile = sendFileList[fileID],
                packetSize = sendFile.curSize;
            if (fileID in sizeCount && sizeCount[fileID] <= 1) {
                packetSize = sizeCount[fileID] === 0 ? sendFile.curSize * 2 : sendFile.curSize + minSize;
                sendFile.curSize = packetSize > maxSize ? maxSize : packetSize;
                console.log(fileID + " add: " + sendFile.curSize);
            }
            clearSizeTimer(fileID);
            setSizeTimer(fileID);
        };

    // 发送计时器
    let senderTimer = [],
        setSenderTimer = function (fileID) {
            senderTimer[fileID] = setTimeout(function () {
                let msg = '<error>传输中断</error>';
                setFileViewMsg(fileID, msg, true);
                socket.emit('file_data_res', {'operate': 'cancel', 'file_id': fileID});
                delete sendFileList[fileID];
            }, transTimeout);
            //console.log("setSenderTimer:" + fileID);
        },
        clearSenderTimer = function (fileID) {
            clearTimeout(senderTimer[fileID]);
            //console.log("clearSenderTimer:" + fileID);
        };

    // 接收计时器
    let receiverTimer = [],
        setReceiverTimer = function (fileID) {
            receiverTimer[fileID] = setTimeout(function () {
                let msg = '<error>传输中断</error>';
                setFileViewMsg(fileID, msg, false);
                socket.emit('file_data_res', {'operate': 'cancel', 'file_id': fileID});
                delete receiveFileList[fileID];
            }, transTimeout);
            //console.log("setReceiverTimer:" + fileID);
        },
        clearReceiverTimer = function (fileID) {
            clearTimeout(receiverTimer[fileID]);
            //console.log("clearReceiverTimer:" + fileID);
        };

    socket.on('connect', function (data) {
        console.log('connect: ' + websocket_url);
        $('#sendFileBtn').removeAttr("disabled");
    });

    socket.on('disconnect', function (data) {
        console.log('disconnect ' + websocket_url);
    });

    // 监听连接成功响应
    socket.on('connect_res', function (data) {
        let code = data.code;
        if (code === 200) {
            SUB = data.data.sub;
        }
    });

    /***********************
     *   文件传输 - 发送端
     ***********************/

    // 监听文件传输响应
    socket.on('sender_res', function (data) {
        let code = data.code, file = data.data, msg = data.msg;
        msg = (code === -1) ? '<error>' + msg + '</error>' : msg;
        msg = (code === 200) ? '<success>' + msg + '</success>' : msg;
        clearSenderTimer(file.id);
        if (code === 100) {
            controlSize(file.id);
            sendFileChunk(file.id, file.start, msg);
            setSenderTimer(file.id);
        } else {
            if (code === 101) {
                sendFileList[file.id].curLoaded = file.start;
                clearSizeTimer(file.id);
                if (msg === '') return;
            }
            setFileViewMsg(file.id, msg, true);
        }
        if (code === 200 || code === -1) {
            delete sendFileList[file.id];
            console.log('清除发送文件缓存', file.id);
            clearSizeTimer(file.id);
        }
    });

    // 监听发送按钮
    $('#sendFileBtn').click(function () {
        let file = $('#fileIpt').get(0).files[0];
        let receiver = $.trim($('#receiverIpt').val());
        if (!file || !receiver) {
            alert('文件或接收者为空');
            console.log('文件或接收者为空');
            return;
        }

        // 用FileReader读取
        let reader = new FileReader(),
            fileID = getRandomString();
        reader.onload = function (e) {
            fileOnload(fileID, e)
        };
        readerList[fileID] = reader;

        // 设置样式并发送文件描述包
        sendFileList[fileID] = {
            id: fileID, // 文件ID
            name: file.name, // 文件名
            size: file.size, // 文件大小
            file: file, // 文件
            sender: SUB, // 发送者
            receiver: receiver, // 接收者
            curLoaded: 0, // 当前传输的字节数
            curSize: minSize, //当前包大小
        };
        setFileView(fileID, true);
        sendFileDesc(fileID);
    });

    // 发送文件描述包
    function sendFileDesc(fileID) {
        let sendFile = sendFileList[fileID],
            descPacket = {
                id: sendFile.id,
                name: sendFile.name,
                size: sendFile.size,
                sender: sendFile.sender,
                receiver: sendFile.receiver,
                state: 0,
            };
        socket.emit('file_desc', descPacket);
        console.log('sendFileDesc', descPacket);
    }

    //指定开始位置，分块读取文件
    function sendFileChunk(fileID, start, msg = '') {
        let sendFile = sendFileList[fileID],
            file = sendFile.file,
            total = sendFile.file.size,
            packetSize = sendFile.curSize;
        if (msg !== '') {
            setFileViewMsg(fileID, msg, true);
        }
        if (start < total) {
            let blob = file.slice(start, start + packetSize);
            readerList[fileID].readAsArrayBuffer(blob);
            sendFile.curLoaded = start;
        }
    }

    // 读取完触发,发送数据包
    function fileOnload(fileID, event) {
        let sendFile = sendFileList[fileID],
            resultConstructor = Uint8Array,
            fileData = new resultConstructor(event.target.result);

        //自定义文件头。
        let idHead = headFor(resultConstructor, fileID);
        let startHead = headFor(resultConstructor, sendFile.curLoaded.toString());
        let lengthHead = headFor(resultConstructor, event.loaded.toString());
        let result = concatenate(resultConstructor, idHead, startHead, lengthHead, fileData).buffer;
        socket.emit('file_data', result);

        sendFile.curLoaded += event.loaded;
        setFileViewPro(fileID, true);
        console.log(fileID + ' send ' + event.loaded);
    }

    // 头部
    function headFor(resultConstructor, item) {
        let head = new resultConstructor(1 + item.length);
        head[0] = item.length;
        for (let i = 0; i < item.length; i++) {
            head[i + 1] = item.charCodeAt(i);
        }
        return head;
    }

    // 合并类型化数组
    function concatenate(resultConstructor, ...arrays) {
        let totalLength = 0;
        for (let arr of arrays) {
            totalLength += arr.length;
        }
        let result = new resultConstructor(totalLength);
        let offset = 0;
        for (let arr of arrays) {
            result.set(arr, offset);
            offset += arr.length;
        }
        return result;
    }

    /***********************
     *   文件传输 - 接收端
     ***********************/

    // 监听文件传输响应
    socket.on('receiver_res', function (data) {
        let code = data.code, file = data.data, msg = data.msg;
        msg = (code === -1) ? '<error>' + msg + '</error>' : msg;
        msg = (code === 200) ? '<success>' + msg + '</success>' : msg;
        clearReceiverTimer(file.id);
        if (code === 0) {
            receiveFileDesc(file);
        } else if (code === 100) {
            receiveFileChunk(file, msg);
            setReceiverTimer(file.id);
        } else {
            if (code === 101) {
                receiveFileList[file.id].curLoaded = file.start;
                if (msg === '') return;
            }
            setFileViewMsg(file.id, msg, false);
        }
        if (code === 200 || code === -1) {
            delete receiveFileList[file.id];
            console.log('清除接收文件缓存', file.id);
        }
    });

    // 回应邀请
    $('.show').on('click', '.fileDescRes', function () {
        let id = $.trim($(this).attr('id'));
        let arr = id.split('_');
        $('#accept' + '_' + arr[1]).remove();
        $('#refuse' + '_' + arr[1]).remove();
        let flag = (arr[0] === 'accept');
        socket.emit('file_desc_res', {'accept': flag, 'file_id': arr[1]});
    });

    // 接受文件描述
    function receiveFileDesc(file) {
        receiveFileList[file.id] = {
            id: file.id, // 文件ID
            name: file.name, // 文件名
            size: file.size, // 文件大小
            sender: file.sender, // 发送者
            receiver: file.receiver, // 接收者
            curLoaded: 0, // 当前传输的字节数
            curSize: minSize, //当前包大小
        };
        setFileView(file.id, false);
        console.log('receiveFileDesc', receiveFileList[file.id])
    }

    // 接收文件
    function receiveFileChunk(file, msg = '') {
        let receiveFile = receiveFileList[file.id],
            total = receiveFile.size;
        if (msg !== '') {
            setFileViewMsg(file.id, msg, false);
        }
        if (file.start === 0) {
            window.open('/download/' + file.id);
            console.log("window.open('/download/" + file.id + "')");
        }
        receiveFile.curLoaded = file.start;
        receiveFile.curSize = file.length;
        setFileViewPro(file.id, false);

        // 发送ack包
        if (file.start >= total) {
            socket.emit('file_complete', {'file_id': file.id});
        }
    }

    /***********************
     *       工具方法
     ***********************/

    // 获得随机字符串来生成文件ID
    function getRandomString() {
        return (Math.random() * new Date().getTime()).toString(36).toUpperCase().replace(/\./g, '-') + '-' + SUB;
    }

    // 设置文件传输显示
    function setFileView(fileID, send = true) {
        let fileData = send ? sendFileList[fileID] : receiveFileList[fileID],
            selector = send ? '#send .show' : '#receive .show',
            title = setString(fileData.name, 40),
            desc = send ? 'TO: ' + fileData.receiver : 'FROM: ' + fileData.sender,
            msg = send ? '请稍等...' :
                '<button class="fileDescRes" id="accept_' + fileID + '">接收</button>' +
                '<button class="fileDescRes" id="refuse_' + fileID + '">拒绝</button>';
        desc += ' | SIZE: ' + byteConvert(fileData.size) + ' ';
        $(selector).append('<li id="file_' + fileID + '">' +
            '        <div class="title">' + title + '</div>' +
            '            <div class="desc">' + desc + '</div>' +
            '            <div class="msg">' + msg + '</div>' +
            '    </li>');
    }

    // 设置文件进度显示
    function setFileViewPro(fileID, send = true) {
        let fileData = send ? sendFileList[fileID] : receiveFileList[fileID],
            id = '#file_' + fileID,
            selector = send ? '#send ' + id + ' .desc' : '#receive ' + id + ' .desc',
            desc = $(selector).text(),
            arr = desc.split('|');
        if (fileData.curLoaded < fileData.size) {
            let percent = fileData.curLoaded / fileData.size * 100,
                progress = 'RATE: ' + percent.toFixed(2) + '%（' + byteConvert(fileData.curSize) + '/s）';
            desc = arr[0] + '|' + arr[1] + '| ' + progress;
            console.log(selector, progress);
        } else {
            desc = arr[0] + '|' + arr[1] + '| RATE: 100.00%';
        }
        $(selector).html(desc);
    }

    // 设置文件消息显示
    function setFileViewMsg(fileID, msg = '', send = true) {
        let id = '#file_' + fileID,
            selector = send ? '#send ' + id + ' .msg' : '#receive ' + id + ' .msg';
        $(selector).html(msg);
        console.log(selector, msg);
    }

    // 监听
    $('.show').on('click', '.fileDataRes', function () {
        let id = $.trim($(this).attr('id')),
            arr = id.split('_');
        let operate = arr[0], fileID = arr[1], start = 0;
        $('#pause' + '_' + fileID).remove();
        $('#continue' + '_' + fileID).remove();
        $('#cancel' + '_' + fileID).remove();
        if (fileID in receiveFileList) {
            start = receiveFileList[fileID].curLoaded
        } else if (fileID in sendFileList) {
            start = sendFileList[fileID].curLoaded
        }
        socket.emit('file_data_res', {'operate': operate, 'file_id': fileID, 'start': start});
    });

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

    // 截取字符串
    function setString(str, len) {
        let strLen = 0, s = '';
        for (let i = 0; i < str.length; i++) {
            if (str.charCodeAt(i) > 128) {
                strLen += 2;
            } else {
                strLen++;
            }
            s += str.charAt(i);
            if (strLen >= len) {
                return s + '...';
            }
        }
        return s;
    }

    function isSender(fileID) {
        if (fileID in sendFileList)
            if (sendFileList[fileID].sender === SUB)
                return true;
        return false;
    }

    function isReceiver(fileID) {
        if (fileID in receiveFileList)
            if (receiveFileList[fileID].receiver === SUB)
                return true;
        return false;
    }
});