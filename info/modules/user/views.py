from flask import render_template, redirect, url_for, request, g, jsonify
from . import user_blue
from info.untils.common import get_data_user
from info import response_code, db
import logging


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

