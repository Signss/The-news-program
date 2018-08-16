from redis import StrictRedis
import logging


# 加载程序配置
class Config(object):
    # 配置调试模式
    DEBUG = True
    #　设置秘钥
    SECRET_KEY = 'xiayong'
    # 指定数据库位置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/news'
    # 禁止追踪数据修改，降低性能损耗
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #　配置redis
    REDIS_HOST = '192.168.138.129'
    REDIS_PORT = 6379
    # 设置Session类型
    SESSION_TYPE = 'redis'
    # 设置Session_rediss使用session存储到redis中
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置标签密文
    SESSION_USE_SIGNER = True
    # 设置Session 过期时间
    PERMANENT_SESSION_LIFETIME = 60*60*24

# 开发环境配置


class DevelopmentConfig(Config):
    DEBUG = True
    LEVE_GRADE = logging.DEBUG

# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False
    LEVE_GRADE = logging.WARNING

# 创建生产和开发配置字典以便加载配置
configs = {
    'dev':DevelopmentConfig,
    'pro':ProductionConfig
}
