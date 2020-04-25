$(function () {
    $('#sub').focus(function () {
        $(this).attr('placeholder', '')
    });

    $('#sub').blur(function () {
        $(this).attr('placeholder', '用户名')
    });

    $('#pwd').focus(function () {
        $(this).attr('placeholder', '')
    });

    $('#pwd').blur(function () {
        $(this).attr('placeholder', '密码')
    });

    $('#login').click(function () {
        if (!$('#sub').val() || !$('#pwd').val()) {
            return;
        }
        $("#login-form").attr("target", "rfFrame");
        $.ajax({
            type: 'POST',
            url: '/login/',
            data: $('#login-form').serialize(),
            dataType: 'json',
            success: function (data) {
                if (data.code === 200) {
                    show_msg(data.msg, 'success')
                    location.href = "/user"
                } else {
                    show_msg(data.msg, 'error')
                }
            },
            error: function (data) {
                show_msg('unknown error', 'error')
            }
        });
    });

    function show_msg(msg, type = '') {
            if (type === 'success') {
                $('#msg').css('background', 'green')
            } else if (type === 'error') {
                $('#msg').css('background', 'red')
            } else {
                $('#msg').css('background', 'black')
            }
            $("#msg").html(msg);
            $("#info").show();
            setTimeout("$('#info').hide()", 2000);
        }
});