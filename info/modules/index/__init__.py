from flask import Blueprint


# 创建蓝图实例对象
index_blur = Blueprint('index',__name__)


from .views import *