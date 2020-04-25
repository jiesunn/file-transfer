$(function () {
    const websocket_url = 'ws://' + document.domain + ':' + location.port + '/home';
    const socket = io.connect(websocket_url);

    socket.on('connect', function (data) {
        console.log(websocket_url, data);
    });

    socket.on('disconnect', function (data) {
        console.log('disconnect');
    });

    // 发送邀请
    $('#submit').click(function () {
        let open_id = $.trim($('#open_id').val());
        if (open_id !== "") {
            socket.emit('invite', {'open_id': open_id});
        }
    });

    // 回应邀请
    $('#show').on('click', '.response', function() {
        let id = $.trim($(this).attr('id'));
        let arr = id.split('_');
        $('#accept' + '_' + arr[1]).remove();
        $('#refuse' + '_' + arr[1]).remove();
        let flag = (arr[0] === 'accept');
        socket.emit('invite_response', {'accept': flag, 'open_id': arr[1]});
    });

    // 监听回复消息
    socket.on('invite_response', function (data) {
        if (data.code === 100) {
            $('#show').append('<li>' + data.msg + '</li>');
        } else if (data.code === 200) {
            $('#show').append('<li class="success">' + data.msg + '</li>');
        } else if (data.code === -1) {
            $('#show').append('<li class="error">' + data.msg + '</li>');
        }
    });
});