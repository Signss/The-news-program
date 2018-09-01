from flask import render_template, redirect, url_for, request, g, jsonify
from . import user_blue
from info.untils.common import get_data_user
from info import response_code, db, constants
import logging
from info.untils.file_storge import upload_file


@user_blue.route('/user_info')
@get_data_user
def user_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    # 构造渲染数据
    context = {
        'user': user.to_dict()
    }
    return render_template('news/user.html', context=context)

# 基本资料接口
@user_blue.route('/base_info', methods=['GET', 'POST'])
@get_data_user
def base_info():

    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        # 构造模板渲染数据
        context = {
            'user': user.to_dict()
        }
        return render_template('news/user_base_info.html', context=context)
    if request.method == 'POST':
        # 接收参数
        # "signature": signature,
        # "nick_name": nick_name,
        # "gender": gender
        signature = request.json.get('signature')
        nick_name = request.json.get('nick_name')
        gender = request.json.get('gender')
        if not all([nick_name, gender, signature]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if gender not in ('MAN', 'WOMAN'):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        # 构造修改数据
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender
        # 同步数据到数据库
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库存储错误')
        # 修改成功的状态返回给前端
        return jsonify(errno=response_code.RET.OK, errmsg='修改成功')


# 上传头像接口
@user_blue.route('/pic_info', methods=['GET', 'POST'])
@get_data_user
def pic_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        context = {
            'user': user.to_dict()
        }
        return render_template('news/user_pic_info.html', context=context)
    if request.method == 'POST':
        avatar_image = request.files.get('avatar')
        if not avatar_image:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        try:
            avatar_image_data = avatar_image.read()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.NODATA, errmsg='读取二进制数据失败')
        # 图片上传到七牛云
        try:
            key = upload_file(avatar_image_data)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='图片上传七牛云失败')
        # 修改用户头像
        user.avatar_url = key
        print(user.avatar_url)
        # 同步数据到数据库
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DATAERR, errmsg='数据同步到数据库失败')
            # 构造响应数据
        data = {
                'avatar_url': constants.QINIU_DOMIN_PREFIX + key
            }
        # 操作成功状态响应给前端
        return jsonify(errno=response_code.RET.OK, errmsg='修改头像成功', data=data)


# 密码修改接口
@user_blue.route('/pass_info', methods=['GET', 'POST'])
@get_data_user
def pass_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    if request.method == 'POST':
        # 接收参数
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')
        if not all([old_password, new_password]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if not user.password_check(old_password):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='原密码错误')
        # 修改用户密码
        user.password = new_password
        # 同步到数据库
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库存储失败')
        return jsonify(errno=response_code.RET.OK, errmsg='修改密码成功')


# 我的收藏接口
# "http://127.0.0.1:5000/user/user_collection?p=1"


