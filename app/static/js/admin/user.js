$(function () {
    let form = layui.form;
    let profile = [];
    form.render();

    function profileIpt(id, show = true) {
        let phone = $('#phone-' + id);
        let email = $('#email-' + id);
        if (show) {
            phone.removeClass('disabled');
            phone.attr('disabled', false);
            email.removeClass('disabled');
            email.attr('disabled', false);
            $('#update-' + id).hide();
            $('#submit-' + id).show();
        } else {
            phone.addClass('disabled');
            phone.attr('disabled', true);
            email.addClass('disabled');
            email.attr('disabled', true);
            $('#update-' + id).show();
            $('#submit-' + id).hide();
        }
    }

    function get_profile(id) {
        return {
            'sub': $('#sub-' + id).html(),
            'phone': $('#phone-' + id).val(),
            'email': $('#email-' + id).val()
        }
    }

    $('.update').click(function () {
        let id = ($(this).attr('id')).split('-')[1];
        profile[id] = get_profile(id)
        profileIpt(id, true)
    });

    $('.submit').click(function () {
        let id = ($(this).attr('id')).split('-')[1],
            data = get_profile(id),
            submit = false;
        $.each(profile[id], function (i, val) {
            if (data[i] !== val) {
                submit = true;
            }
        })
        delete profile[id];
        if (!submit) {
            profileIpt(id, false)
            return;
        }
        $.ajax({
            type: 'POST',
            url: '/admin/user/profile',
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.code === 200) {
                    layer.msg(data.msg);
                    profileIpt(id, false)
                } else {
                    layer.msg(data.msg);
                }
            },
            error: function (data) {
                layer.msg('服务器端错误');
            }
        });
    });

    form.on('switch(pid-switch)', function (data) {
        let id = (data.elem.id).split('-')[1],
            sub = $('#sub-' + id).html(),
            checked = data.elem.checked,
            msg = '确定要开启用户' + sub + '的管理员权限吗？',
            pid = 2;
        if (!checked) {
            msg = '确定要关闭用户' + sub + '的管理员权限吗？';
            pid = 1;
        }
        data.elem.checked = !checked;
        form.render();
        layer.alert(msg, {
            title: '权限更改提示',
            btn: ['确定', '取消'],
            yes: function (index) {
                $.ajax({
                    type: 'POST',
                    url: '/admin/user/pid',
                    data: {'sub': sub, 'pid': pid},
                    dataType: 'json',
                    success: function (res) {
                        if (res.code === 200) {
                            data.elem.checked = checked;
                            form.render();
                        }
                        layer.msg(res.msg);
                    },
                    error: function (data) {
                        layer.msg('服务器端错误');
                    }
                });
                layer.close(index);
            },
            btn2: function (index) {
                layer.close(index);
            }
        });
    });

    form.on('submit(query-submit)', function (form) {
        $.ajax({
            type: 'POST',
            url: '/admin/user/query',
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