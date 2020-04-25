$(function () {
    let form = layui.form;
    form.render();

    form.on('submit(query-submit)', function (form) {
        $.ajax({
            type: 'POST',
            url: '/admin/log/query',
            data: form.field,
            dataType: 'json',
            success: function (data) {
                if (data.code === 200) {
                    location.href = data.data.url
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
});