$.ajaxSetup({
    error : function(xhr, textStatus, error) {
        var err_code = xhr.status;
        switch (err_code) {
        case 404:
            alert('页面没有找到.');
            break;
        case 500:
            alert('服务器发生错误, 请稍后再试.');
            break;
        case 405:
            alert('缺少必须的请求参数.');
            break;
        default:
            alert('请求发生错误.');
            break;
        }
    },
    beforeSend : function(xhr) {
        if (!(document.cookie || navigator.cookieEnabled)) {
            alert('您的浏览器关闭了cookie功能, 这样可能会影响您在本站的体验.');
        }
    }
});
function un_favo() {
    if (!$(':checked').length) {
        return false;
    }
    $.post('/user/unfavo', $('#shelf_frm').serialize(), function(data) {
        data = eval("(" + data + ")");
        if (data['succ']) {
            window.document.location = window.document.location;
        } else {
            alert('操作失败, 请稍后再试');
        }
    });
}
function confirm_clean(msg) {
    if (confirm(msg)) {
        $.get('/user/unfavoall', function(data) {
            data = eval("(" + data + ")");
            if (data['succ']) {
                window.document.location = window.document.location;
            } else {
                alert('操作失败, 请稍后再试');
            }
        });
    }
}
function selectall() {
    var v = document.getElementsByName('u_books');
    for ( var i = 0; i < v.length; i++) {
        v[i].checked = true;
    }
}
function selectleft() {
    var v = document.getElementsByName('u_books');
    for ( var i = 0; i < v.length; i++) {
        v[i].checked = !v[i].checked;
    }
}

$(function() {
    var counts = $('.update_count');
    if (!counts.length) {
        return;
    }
    var book_ids = "";
    counts.each(function() {
        book_ids = book_ids + $(this).attr('val') + ",";
    });
    if (book_ids) {
        book_ids = book_ids.substring(0, book_ids.length);
        $.get("/common/buc?book_ids=" + book_ids, function(data) {
            data = eval("(" + data + ")");
            counts.each(function() {
                var bid = $(this).attr('val');
                $(this).html(data[bid]);
            });
        });
    }
});

function add_favo(b_id) {
    $.get("/user/favo/" + b_id, function(data) {
        data = eval("(" + data + ")");
        if (data['succ']) {
            alert('收藏成功');
        } else {
            alert('收藏失败, 请稍后再试');
        }
    });
}
function login_reg_func() {
    var user_name = $('#user_name').val();
    if (!user_name || !$.trim(user_name)) {
        alert("用户名不能为空");
        return false;
    }
    $('#user_name').val($.trim(user_name));
    var pass_word = $('#pass_word').val();
    if (!pass_word || !$.trim(pass_word)) {
        alert("密码不能为空");
        return false;
    }
    $.post("/authority", $("#login_reg").serialize(), function(data) {
        data = eval("(" + data + ")");
        if (data['succ']) {
            if (data['code'] == 1) {
                alert("本站自动为你创建了账户: " + data['curr_user']['user_name']
                        + ", 如果您在当前使用的电脑上有临时书架, 本站将自动将其同步到永久书架.");
                window.document.location = "/shelf";
            }
            if (data['code'] == 2) {
                window.document.location = "/shelf";
            }
        } else {
            if (data['code'] == 0) {
                alert("账号或密码不能为空");
                return;
            }
            if (data['code'] == 2) {
                alert("服务器出错, 自动创建账号失败, 请稍后再试");
                return;
            }
            if (data['code'] == 3) {
                alert("密码错误");
                return;
            }
        }
    });
}

function add_bookinfo_func() {
    var book_name = $('#book_name').val();
    if (!book_name || !$.trim(book_name)) {
        alert("小说名不能为空");
        return false;
    }
    $('#book_name').val($.trim(book_name));
    $.post("/common/bookinfo/save", $("#add_bookinfo").serialize(), function(data) {
        data = eval("(" + data + ")");
        if (data['succ']) {
            alert('提交成功');
            window.document.location.reload();
        } else {
            if (data['code'] == 0) {
                alert("小说名或首发站不能为空");
                return;
            }
            if (data['code'] == 1) {
                alert("请不要提交本站不支持的首发站点.");
                return;
            }
            if (data['code'] == 2) {
                alert("提交失败, 请稍后再试");
                return;
            }
            if (data['code'] == 3) {
                alert("本书已收录");
                window.document.location = '/book/' + data['b_id']
                return;
            }
            if (data['code'] == 4) {
                alert("请勿重复提交");
                return;
            }
        }
    });
}
