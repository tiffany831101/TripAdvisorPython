from flask import current_app, jsonify, make_response, flash
from . import api
from tripadvisor import redis_store
from tripadvisor.utlis.captcha.captcha import captcha
from tripadvisor.settings.defaults import *

@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    功能 : 獲取圖片驗證碼
    參數 : image_code_id: 圖片驗證碼編號
    返回 : 驗證碼圖片
    """
    
    text, image_data = captcha.generate_captcha()
    try:    
        redis_store.setex("image_code_%s"%image_code_id, IMAGR_CODE_REDIS_EXPRIES, text)
    except Exception as e:
        current_app.logger.error(e)

    response = make_response(image_data)
    response.headers["Content-Type"]="image/jpg"
    return response