from flask import jsonify, make_response
import logging

from . import api
from tripadvisor import redis_store
from tripadvisor.utlis.captcha.captcha import captcha
from tripadvisor.settings.defaults import IMAGR_CODE_REDIS_EXPRIES


logger = logging.getLogger()

@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """獲取圖片驗證碼"""
    
    text, image_data = captcha.generate_captcha()
    try:    
        redis_store.setex(f"image_code_{image_code_id}", IMAGR_CODE_REDIS_EXPRIES, text)
    except Exception as e:
        logger.error(e)

    response = make_response(image_data)
    response.headers["Content-Type"]="image/jpg"
    return response