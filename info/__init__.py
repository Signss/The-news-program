from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from redis import StrictRedis
from config import configs
from flask_wtf import CSRFProtect, csrf
import logging


# 创建一个空的redis实例对象
redis_store = None  # type:StrictRedis

# 创建一个空的db实例对象
db = SQLAlchemy()


def setup_log(level):
    # 设置日志的记录等级。
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    # 创建flask 实例对象
    app = Flask(__name__)
    # 获取配置类型
    config_class = configs[config_name]
    app.config.from_object(config_class)
    # CRSF保护
    CSRFProtect(app)
    # 创建数据库对象
    db.init_app(app)
    # 　创建Session
    Session(app)
    # 调用日志函数
    setup_log(config_class.LEVE_GRADE)
    # 创建redis实例对象，让session存储在redis中
    global redis_store
    redis_store = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, decode_responses=True)
    # 注册蓝图
    from info.modules.index import index_blur
    app.register_blueprint(index_blur)
    # 注册注册模块蓝图
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    # 注册新闻详情页蓝图
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    # 开启csrf保护
    @app.after_request
    def after_request(response):
        # 该方法自动生成csrf_token值并在session中存储一份，csrf
        # 　保护会自动从表单或请求头中去找csrf_token值
        csrf_token = csrf.generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    # 自定义过滤器
    from info.untils.common import do_rank
    app.add_template_filter(do_rank, 'rank')
    return app
