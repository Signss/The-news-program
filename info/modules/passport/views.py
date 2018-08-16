from flask import request,abort,make_response,jsonify,session
from . import passport_blue
from info.untils.captcha.captcha import captcha
from info import redis_store,constants,response_code,db
import logging,re,random,datetime
from info.libs.yuntongxun.sms import Cpp
from info.models import User


# 生成图片验证码
@passport_blue.route('/image_code')
def get_image_code():
    # 1 获取前端发送的参数uuid
    image_code = request.args.get('imageCodeId')
    # 2 判断参数是否存在
    if not image_code:
        abort(400)
    # 3 生成图片验证码
    name,text,image = captcha.generate_captcha()
    # 4 把生成的图片验证码存储到redis以便发送短信验证码时判断用户的图片验证码是否正确
    try:
        redis_store.set('ImageCode:'+image_code,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        abort(500)
    # 5 把图片验证码发送给前端
    response = make_response(image)
    response.headers['Content-Type']='image/jpg'
    return response


# 生成短信验证码
@passport_blue.route('/sms_code',methods=['POST'])
def get_sms_code():
    # 1接收参数
    json_dict = request.json
    mobile = json_dict.get('mobile')
    imageCode_client = json_dict.get('imageCode')
    imageCodeId = json_dict.get('imageCodeId')
    # 2校验参数
    if not all([mobile,imageCode_client,imageCodeId]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数不全')
    # 3判断手机号是否合法
    if not re.match('^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\d{8}$',mobile).group():
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='手机号码不合法')
    # 4 从redis中取出用户的图片验证码，看与前台输入的验证码是否一致
    try:
        server_imageCode = redis_store.get('ImageCode:'+imageCodeId)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DATAERR,errmsg='redis数据库错误')
    # ５　判断图片验证码是否过期
    if not server_imageCode:
        return jsonify(errno=response_code.RET.DATAERR,errmsg='图片验证码已过期')
    # 6 判断前端发送的图片验证码与服务器存储的验证码是否一致
    if imageCode_client.lower() != server_imageCode.lower():
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='图片验证码错误')
    # 7 生成短信验证码
    sms_code = '%06d'%random.randint(0,999999)

    # # 9 发送短信验证码
    # result = Cpp().send_to_sms(mobile,[sms_code,5],1)
    # if result != 0:
    #     return jsonify(errno=response_code.RET.THIRDERR,errmsg='第三方容联云错误')
    # # 9 把短信验证码存储到redis中以便验证下一步验证短信验证码
    # try:
    #     redis_store.set('smsCode:'+mobile, sms_code)
    # except Exception as e:
    #     logging.error(e)
    #     return jsonify(errno=response_code.RET.DATAERR,errmsg='redis数据库错误')
    # # 10　把短信验证码是否发送成功的状态返回
    # return jsonify(errno=response_code.RET.OK,errmsg='短信发送成功')


# 注册功能
@passport_blue.route('/register',methods=['POST'])
def register():
    # 1 获取参数
    json_dict = request.json
    mobile = json_dict.get('mobile')
    smscode_client = json_dict.get('smscode')
    password = json_dict.get('password')
    # 2 判断参数
    if not all([mobile,smscode_client,password]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数错误')
    # 3手机号码是否合法
    if not re.match('^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\d{8}$',mobile).group():
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='手机号码不合法')
    # 4从redis中取出短信验证码与前台验证码对比
    # try:
    #     smscode_server = redis_store.get('smsCode:'+mobile)
    # except Exception as e:
    #     logging.error(e)
    #     return jsonify(errno=response_code.RET.DATAERR,errmsg='短信验证码错误')
    # # 5 判断图片验证码是否过期
    # if not smscode_server:
    #     return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数错误')
    # # 6 判断前后端验证码是否一致
    # if smscode_client != smscode_server:
    #     return jsonify(errno=response_code.RET.PARAMERR,errmsg='短信验证码错误')
    # 7 创建用户对象
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    # 密码做密文处理
    user.password = password
    logging.debug(user.password_hash)
    # 8 记录最后一次登陆时间做为状态保持
    user.last_login = datetime.datetime.now()
    # 9　把数据加到mysql数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='注册失败')
    # 10 状态保持
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    # 11给前台返回登陆成功状态
    return jsonify(errno=response_code.RET.OK,errmsg='注册成功')


# 登陆接口
@passport_blue.route('/login',methods=['POST'])
def login():
    # 1 获取参数
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')
    # 2判断参数
    if not all([mobile,password]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数错误')
    # 3判断手机号码是否合法
    if not re.match('^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\d{8}$',mobile).group():
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='账号或密码错误')
    # 4判断用户是否存在
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='账号或密码错误')
    if not user:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='账号或密码错误')
    # 5 密码对比
    if not user.password_check(password):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='密码错误')
    user.last_login = datetime.datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='登陆失败')

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    # 6 把登陆成功的状态返回
    return jsonify(errno=response_code.RET.OK,errmsg='登陆成功')


# 退出接口
@passport_blue.route('/logout')
def logout():
    #　核心清除session
    session.pop('user_id',None)
    session.pop('mobile',None)
    session.pop('nick_name',None)
    # 把状态返回给前台
    return jsonify(errno=response_code.RET.OK,errmsg='登出成功')


