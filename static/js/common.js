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
