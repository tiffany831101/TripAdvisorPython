from . import api
from app import constants, redis_store
from flask import current_app, jsonify, make_response, flash
from app.utlis.captcha.captcha import captcha
import random
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    獲取圖片驗證碼
    : params image_code_id: 圖片驗證碼編號
    return : 驗證碼圖片
    """
    #  業務邏輯處理 : 
    #  1. 生成驗證碼圖片
    #　返回名字、真實文本、圖片數據
    text, image_data = captcha.generate_captcha()
    #  2. 將驗證碼真實值與編號保存到redis中
    #  3. 返回圖片
    #  單條維護記錄，選用字符串
    # redis_store.set("image_code_%s" % image_code_id, text)
    # redis_store.expire("image_code%s" % image_code_id, constants.IMAGR_CODE_REDIS_EXPRIES)
    try:    
        redis_store.setex("image_code_%s"%image_code_id, constants.IMAGR_CODE_REDIS_EXPRIES, text)
    except Exception as e:
    #     # 紀錄日誌
        current_app.logger.error(e)
        
    # 返回圖片
    response = make_response(image_data)
    response.headers["Content-Type"]="image/jpg"
    return response