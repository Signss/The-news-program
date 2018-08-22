function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault()

        //TODO 上传头像
        // ajaxSubmit : 模拟表单的读取数据的方式，让表单自己收集数据，可以不用自己写代码读取表单中的数据
        // 使用场景：如果表单中不仅仅需要收集文字信息时需要使用，比如表单中需要收集文件，比如表单中需要收集文件和文字
        // 如果表单中需要收集纯文字，只需要使用$.ajax()
        $(this).ajaxSubmit({
            url: "/user/pic_info",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    // 更新用户的所有头像
                    $(".now_user_pic").attr("src", resp.data.avatar_url);
                    $(".user_center_pic>img", parent.document).attr("src", resp.data.avatar_url);
                    $(".user_login>img", parent.document).attr("src", resp.data.avatar_url);
                }else {
                    alert(resp.errmsg);
                }
            }
        });
    })
})