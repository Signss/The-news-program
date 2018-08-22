from qiniu import Auth, put_data


access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'

def upload_file(data):
    """
        上传文件到七牛云
        :param data: 要上传的文件的二进制
        :return: Fg-7WDaDihkttxOclQqZkMC3KUqf
        """
    q = Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = put_data(token, None, data)
    if info.status_code != 200:
        raise Exception('上传图片失败')
    return ret.get('key')