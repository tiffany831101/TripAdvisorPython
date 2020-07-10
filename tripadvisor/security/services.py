from flask import render_template, redirect, request, url_for, flash, make_response, jsonify, session, current_app
from flask_login import login_user

import logging
import re

from tripadvisor.models import User
from tripadvisor import db, redis_store
from tripadvisor.settings.defaults import *

logger = logging.getLogger()


def check_login_failuer_num(user_ip):
    status = {}
    try:
        login_failure_nums = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        logger.error(e)
    else:
        if login_failure_nums is not None and int(login_failure_nums) >= LOGIN_ERROR_MAX_TIMES:
            status["status"] = "error"
            status["errmsg"] = "錯誤次數過多，請稍後重試"
    return status, login_failure_nums


def check_password(user, password, user_ip, login_failure_nums):
    status = {}
    if user is None or user.verify_password(password) is False:
        try:
            status["status"] = "error"
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, LOGIN_ERROR_FORBID_TIME)
            if login_failure_nums is None:
                status["errmsg"] = "用戶名或密碼錯誤，您還剩下4次登入機會"
                return status

            n = 4 - int(login_failure_nums)

            if n !=0:
                status["errmsg"] = "用戶名或密碼錯誤，您還剩下%s次登入機會"%n
                return status
            else:
                status["errmsg"] = "錯誤次數過多，請五分鐘後再試"
                return status

        except Exception as e:
            logger.error(e)
            status["errmsg"] = "redis數據庫錯誤"
            return status
    

def set_login_session(user, password, remember_me):
    if user is not None and user.verify_password(password):
        login_user(user, remember_me)
        session["cellphone"] = user.cellphone
        session["username"] = user.username
        response = make_response(jsonify({'errno':1,'errmsg':'數據查詢成功'}))
        response.set_cookie("username",user.username)
        return response


def check_captcha(image_code_id, image_code):
    status = {}

    if not all ([image_code_id,image_code]):
        status["status"] = "error"
        status["errmsg"] = "請輸入驗證碼！"
        return status

    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        logging.error(e)
        status["status"] = "error"
        status["errmsg"] = "內部系統錯誤，請再試一次"
        return status
    
    if real_image_code is None:
        status["status"] = "error"
        status["errmsg"] = "圖片驗證碼失效，請再試一次"
        return status

    try:
        redis_store.delete("image_code_%s" %image_code_id)
    except Exception as e:
        logger.error(e)

    if real_image_code.lower() != image_code.lower():
        status["status"] = "error"
        status["errmsg"] = "圖片驗證錯誤"
        return status


def check_register_info(cellphone, password, password2, email, username):
    status = {}
    if not re.match(r"[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$",email):
        status["status"] = "error"
        status["errmsg"] = "請輸入正確的Email"
        return status

    if not re.match(r"^09\d{8}$",cellphone):
        status["status"] = "error"
        status["errmsg"] = "請輸入正確的手機號格式"
        return status


def check_double_register(username, email, cellphone):
    status = {}
    if User.find_by_username(username):
        status["status"] = "error"
        status["errmsg"] = "該用戶名已被註冊過"
        return status

    if User.find_by_email(email):
        status["status"] = "error"
        status["errmsg"] = "該信箱已註冊過"
        return status

    if User.find_by_cellphone(cellphone):
        status["status"] = "error"
        status["errmsg"] = "該手機號已註冊過"
        return status


def save_register(username, email, cellphone, password):
    status = {}
    user = User(username=username, email=email, cellphone=cellphone, password =password)

    try:
        db.session.add(user)
        db.session.commit()
        status["status"] = "success"
        status["msg"] = "數據保存成功"
        return status

    except Exception as e:
        db.session.rollback()
        logger.error(e)

        status["status"] = "error"
        status["msg"] = "內部系統錯誤，請再試一次"
        return status
