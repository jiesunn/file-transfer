$(function () {
    let form = layui.form;
    let element = layui.element;

    //表单验证
    form.verify({
        pwd: [
            /^[\S]{6,12}$/
            , '密码必须6到12位，且不能出现空格'
        ]
    });

    //监听更改信息提交
    form.on('submit(profile-submit)', function (form) {
        $.ajax({
            type: 'POST',
            url: '/home/profile',
            data: form.field,
            dataType: 'json',
            success: function (data) {
                if (data.code === 200) {
                    layer.msg(data.msg);
                    location.reload()
                } else {
                    layer.msg(data.msg);
                }
            },
            error: function (data) {
                layer.msg('服务器端错误');
            }
        });
        return false
    });

    //监听更改密码提交
    form.on('submit(pwd-submit)', function (form) {
        $.ajax({
            type: 'POST',
            url: '/home/pwd',
            data: form.field,
            dataType: 'json',
            success: function (data) {
                if (data.code === 200) {
                    layer.msg(data.msg);
                    location.reload()
                } else {
                    layer.msg(data.msg);
                }
            },
            error: function (data) {
                layer.msg('服务器端错误');
            }
        });
        return false
    });
})
