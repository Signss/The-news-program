from flask import Blueprint


# 实例化蓝图对象
passport_blue = Blueprint('passport',__name__,url_prefix='/passport')


from .views import *
