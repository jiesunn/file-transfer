$(function () {
    let element = layui.element;

    // 建立ws连接
    const websocket_url = 'ws://' + document.domain + ':' + location.port + '/wsFile',
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
                setFileViewPro(fileID, -1, true);
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
                setFileViewPro(fileID, -1, false);
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
        console.log(data)
        let code = data.code;
        if (code === 200) {
            SUB = data.data.sub;
        }
    });

    /***********************
     *   选择文件
     ***********************/

    $("#fileIptMine").bind("click", function () {
        return $("#fileIpt").click();
    })

    $("#fileIpt").bind("change", function () {
        let filePath = $(this).val();
        console.log(filePath)
        let fileName = "未上传文件"
        if (filePath) {
            let arr = filePath.split('\\');
            fileName = arr[arr.length - 1];
            fileName = setString(fileName, 15)
        }
        $(".showFileName").html(fileName);
    })

    /***********************
     *   文件传输 - 发送端
     ***********************/

    // 监听文件传输响应
    socket.on('sender_res', function (data) {
        console.log(data)
        let code = data.code, file = data.data, msg = data.msg;
        msg = (code === -1) ? '<error>' + msg + '</error>' : msg;
        msg = (code === 200) ? '<success>' + msg + '</success>' : msg;
        clearSenderTimer(file.id);
        if (code === 100) {
            controlSize(file.id);
            sendFileChunk(file.id, file.start, msg);
            setSenderTimer(file.id);
        } else if (code === 101) {
            sendFileList[file.id].curLoaded = file.start;
            clearSizeTimer(file.id);
        } else if (code === 200 || code === -1) {
            delete sendFileList[file.id];
            console.log('清除发送文件缓存', file.id);
            clearSizeTimer(file.id);
        }
        setFileViewPro(file.id, code, true)
        setFileViewMsg(file.id, msg, true);
    });

    // 监听发送按钮
    $('#sendFileBtn').bind("click", function () {
        let file = $('#fileIpt').get(0).files[0];
        let receiver = $.trim($('#receiverIpt').val());
        if (!file || !receiver) {
            layer.msg('文件或接收者为空');
            return;
        }

        // 用FileReader读取
        let reader = new FileReader(),
            fileID = getRandomString();
        reader.onload = function (e) {
            fileOnload(fileID, e);
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
                cur: 0,
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
            let selector = '#receive #file_' + file.id + ' .layui-progress-bar';
            $(selector).attr('class', 'layui-progress-bar layui-bg-green');
            receiveFileChunk(file, msg);
            setReceiverTimer(file.id);
        } else if (code === 101) {
            receiveFileList[file.id].curLoaded = file.start;
            if (msg === '') return;
        } else if (code === 200 || code === -1) {
            delete receiveFileList[file.id];
            console.log('清除接收文件缓存', file.id);
        }
        setFileViewPro(file.id, code, false);
        setFileViewMsg(file.id, msg, false);
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
            //window.open('/file/download/' + file.id);
            $("#ifile").attr('src', '/file/download/' + file.id)
            console.log("window.open('/file/download/" + file.id + "')");
        }
        receiveFile.curLoaded = file.start;
        receiveFile.curSize = file.length;

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
                '<button class="fileDescRes accept" id="accept_' + fileID + '">接收</button>' +
                '<button class="fileDescRes refuse" id="refuse_' + fileID + '">拒绝</button>';
        desc += ' | SIZE: ' + byteConvert(fileData.size) + ' ';
        $(selector).append('<li id="file_' + fileID + '">' +
            '<div class="layui-progress" lay-filter="' + fileID + '">' +
            '<div class="layui-progress-bar layui-bg-green" lay-percent="0%"></div></div>' +
            '<div class="title">' + title + '</div>' +
            '<div class="desc">' + desc + '</div>' +
            '<div class="file-msg">' + msg + '</div>' +
            '</li></div>');
    }

    // 设置文件进度显示
    function setFileViewPro(fileID, code = 200, send = true) {
        let color = {
            '200': 'layui-bg-green',
            '100': 'layui-bg-green',
            '101': 'layui-bg-orange',
            '-1': 'layui-bg-red',
        }
        let id = '#file_' + fileID,
            fileData = send ? sendFileList[fileID] : receiveFileList[fileID],
            selector_pro = send ? '#send ' + id + ' .layui-progress-bar' : '#receive ' + id + ' .layui-progress-bar';
        $(selector_pro).attr('class', 'layui-progress-bar ' + color[code.toString()])
        if (!fileData || !'curLoaded' in fileData) {
            return
        }

        let selector_desc = send ? '#send ' + id + ' .desc' : '#receive ' + id + ' .desc',
            arr = $(selector_desc).text().split('|'),
            desc = arr[0] + '|' + arr[1],
            progress = '100%';
        if (fileData.curLoaded < fileData.size) {
            let percent = fileData.curLoaded / fileData.size * 100,
                rate = 'Rate: ' + byteConvert(fileData.curSize) + '/s';
            desc += '| ' + rate;
            progress = percent.toFixed(2) + '%';
        }
        element.progress(fileID, progress);
        $(selector_desc).html(desc);
        console.log(selector_desc, progress, desc);
    }

    // 设置文件消息显示
    function setFileViewMsg(fileID, msg = '', send = true) {
        if (!fileID || !msg) {
            return;
        }
        let id = '#file_' + fileID,
            selector = send ? '#send ' + id + ' .file-msg' : '#receive ' + id + ' .file-msg';
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
});