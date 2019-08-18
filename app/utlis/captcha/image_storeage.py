
from qiniu import Auth, put_data, etag, urlsafe_base64_encode
import qiniu.config

access_key=
secret_key=

def storage(file_data):
    q= Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name =""

    token = q.upload_token(bucket_name, key, 360)

    localfile = './sync/bbb.jpg'
    ret, info = put_data(token, None, localfile)
    if info.status_code == 200:
        # 表示上传成功，返回文件名
        return ret.get("key")
    else:
        # 上传失败
        raise Exception("上传七牛失败")
    



if __name__=='__main__':
    storage(file_data)