# -*- coding:utf-8 -*-

from info.libs.yuntongxun.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8aaf07086521916801652d2162d1072a'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = 'db0fc295cfe44b0b88eb99fa527c21e7'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf07086521916801652d2163270730'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'sandboxapp.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'

# 云通讯官方提供的发送短信代码实例
# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(_serverIP, _serverPort, _softVersion)
#     rest.setAccount(_accountSid, _accountToken)
#     rest.setAppId(_appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.items():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print('%s:%s' % (k, s))
#         else:
#             print('%s:%s' % (k, v))

# 使用单例模式降低性能损耗
class Cpp(object):
    def __new__(cls,*args, **kwargs):
        if not hasattr(cls,'__instance'):
            cls.__instance = super(Cpp, cls).__new__(cls)

            cls.__instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls.__instance.rest.setAccount(_accountSid, _accountToken)
            cls.__instance.rest.setAppId(_appId)
        return cls.__instance

    def send_to_sms(self,to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        if result.get('statusCode') != '000000':
            return -1
        else:
            return 0


# if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    # sendTemplateSMS('18601927460', ['789456', 5], 1)
    # Cpp().send_to_sms('18601927460', ['123456', 5], 1)