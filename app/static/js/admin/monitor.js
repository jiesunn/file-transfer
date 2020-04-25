$(function () {
    // 每5s刷新数据
    let count = 5
    query();

    setInterval(query, count * 1000);
    setInterval(function () {
        $("#clock").html("还剩 " + count.toString() + "s 刷新");
        count--;
    }, 1000);

    function query() {
        $.ajax({
            type: 'POST',
            url: '/admin/monitor/query',
            data: {},
            dataType: 'json',
            success: function (data) {
                $("#tbody").html('');
                if (data.code === 200) {
                    $("#null").hide();
                    show(data.data)
                } else {
                    $("#null").show();
                }
            },
            error: function (data) {
                layer.msg('服务器端错误');
            }
        });
        count = 5
        $("#time").html("刷新时间：" + getTime())
    }

    function show(list) {
        for (let i = 0; i < list.length; i++) {
            let data = JSON.parse(list[i])
            console.log(data)
            let progress = (data.cur / data.size * 100).toFixed(2) + '%';
            let state = '<span class="layui-badge">中断</span>'
            if (data.state === 0) {
                state = '<span class="layui-badge layui-bg-green">正常</span>'
            } else if (data.state === 1) {
                state = '<span class="layui-badge layui-bg-orange">暂停</span>'
            }
            let html = '<tr><td>' + data.id + '</td>' +
                '<td>' + data.name + '</td>' +
                '<td>' + byteConvert(data.size) + '</td>' +
                '<td>' + progress + '</td>' +
                '<td>' + state + '</td>' +
                '<td>' + data.sender + '</td>' +
                '<td>' + data.receiver + '</td></tr>'
            $("#tbody").append(html);
        }
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

    function getNow(s) {
        return s < 10 ? '0' + s : s;
    }

    function getTime() {
        let myDate = new Date();
        let year = myDate.getFullYear();        //获取当前年
        let month = myDate.getMonth() + 1;   //获取当前月
        let date = myDate.getDate();            //获取当前日
        let h = myDate.getHours();              //获取当前小时数(0-23)
        let m = myDate.getMinutes();          //获取当前分钟数(0-59)
        let s = myDate.getSeconds();
        return year + '-' + getNow(month) + "-" + getNow(date) + " " + getNow(h) + ':' + getNow(m) + ":" + getNow(s);
    }
});