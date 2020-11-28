from flask import render_template, redirect, request, url_for, flash, Response, jsonify, session, current_app
from flask_login import login_user

import logging
import re

from tripadvisor.models import User
from tripadvisor import db, redis_store, dao
from tripadvisor.settings.defaults import *

logger = logging.getLogger()
EMAIL_FORMAT = r"[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$"
PHONE_FORMAT = r"^09\d{8}$"


def check_login_failuer_num(user_ip):
    status = {}
    try:
        login_failure_nums = redis_store.get(f"access_num_{user_ip}")
    except Exception as e:
        logger.error(e)
    else:
        if login_failure_nums is not None and int(login_failure_nums) >= LOGIN_ERROR_MAX_TIMES:
            status["status"] = "error"
            status["errmsg"] = "錯誤次數過多，請稍後重試"
    return status, login_failure_nums


def check_password(user, password, user_ip, login_failure_nums):
    status = {}
    if not user or user.verify_password(password) is False:
        try:
            status["status"] = "error"
            redis_store.incr(f"access_num_{user_ip}")
            redis_store.expire(f"access_num_{user_ip}", LOGIN_ERROR_FORBID_TIME)
            if not login_failure_nums:
                status["errmsg"] = "用戶名或密碼錯誤，您還剩下4次登入機會"
                return status

            n = 4 - int(login_failure_nums)

            if n !=0:
                status["errmsg"] = f"用戶名或密碼錯誤，您還剩下{n}次登入機會"
                return status
            else:
                status["errmsg"] = "錯誤次數過多，請五分鐘後再試"
                return status

        except Exception as e:
            logger.error(e)
            status["errmsg"] = "redis數據庫錯誤"
            return status
    

def set_login_session(data):
    user = User().find_by_email(data['email'])
    if user and user.verify_password(data['password']):
        if 'remember_me' in data:
            login_user(user, data['remember_me'])
        else:
            login_user(user)

        session['cellphone'] = user.cellphone
        session['username']  = user.username
    

def check_captcha(image_code_id, image_code):
    if not all ([image_code_id, image_code]):
        return '請輸入驗證碼！'

    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
    except Exception as e:
        logging.error(e)
        return '內部系統錯誤，請再試一次'
    
    if not real_image_code:
        return '圖片驗證碼失效，請再試一次'

    try:
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        logger.error(e)

    if real_image_code.lower() != image_code.lower():
        return '圖片驗證錯誤'


def check_register_info(**kwargs):
    if 'email' in kwargs and not re.match(EMAIL_FORMAT, kwargs['email']):
        return '請輸入正確的Email'

    if 'cellphone' in kwargs and not re.match(PHONE_FORMAT, kwargs['cellphone']):
        return '請輸入正確的手機號格式'


def check_double_register(**kwargs):
    status = {}
    user = User()
    if 'username' in kwargs and user.find_by_username(kwargs['username']):
        return '該用戶名已被註冊過'

    if 'email' in kwargs and user.find_by_email(kwargs['email']):
        return '該信箱已註冊過'
    
    if 'cellphone' in kwargs and user.find_by_cellphone(kwargs['cellphone']):
        return '該手機號已註冊過'


def check_parmas(data, user_ip):
    is_error, login_failure_nums = check_login_failuer_num(user_ip)

    if is_error:
        return is_error

    try:
        user = User()
        user = user.find_by_email(data["email"])
    except Exception as e:
        return {"status":"error", "errmsg":"請再次確認Email或密碼是否正確"}

    is_error = check_password(user, data["password"], user_ip, login_failure_nums)
    
    if is_error:
        return is_error


def user_register(**kwargs):
    isError = check_captcha(kwargs['image_code_id'], kwargs['image_code'])
    if isError:
        return isError

    isError = check_register_info(**kwargs)
    if isError:
        return isError

    isError = check_double_register(**kwargs)
    if isError:
        return isError

    user = User(username = kwargs['username'],
                email = kwargs['email'], 
                cellphone = kwargs['cellphone'], 
                password = kwargs['password'])
    dao.save(user)


def verification(data):
    isError = check_captcha(data['image_code_id'], data['image_code'])
    user = User().find_by_cellphone_and_email(data['cellphone'], data['email'])
    return isError, user


def update_password(data):  
    user = User().find_by_email(data['email'])

    if user:
        user.password = data['password']
        dao.save(user)
    else:
        return '請再試一次'


def update_info(data, current_user):
    isError = check_double_register(username=data['username'])
    if isError:
        return isError
        
    isError = check_register_info(**data)
    if isError:
        return isError

    user = User().update(current_user.id, **data)

    return user