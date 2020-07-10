from flask import render_template, redirect, request, url_for, flash, make_response, jsonify, session, current_app
from flask_login import login_required, current_user, logout_user
from flask_datepicker import datepicker

from wtforms import Form
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from werkzeug.utils import secure_filename
import json
import logging
import os
import re

from tripadvisor.security import auth, services
from tripadvisor.models import User
from tripadvisor.email import send_message
import tripadvisor.settings.defaults
from tripadvisor.security.forms import LoginForm, RegistrationForm, PasswordResetForm, \
                                    UserInfomationForm, UploadImageForm, UpdateInfoForm
from tripadvisor import db, photos, redis_store, CSRFProtect
from tripadvisor.settings.defaults import *


logger = logging.getLogger()


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login/html',methods=["POST","GET"])
def login_html():
    return render_template('auth/login.html')


@auth.route('/login',methods=["POST"])
def login():
    """登入功能"""
    email = request.form.get("email")
    password = request.form.get("password")
    remember_me = request.form.get("remember_me")
    user_ip = request.remote_addr

    check_error, login_failure_nums = services.check_login_failuer_num(user_ip)

    if check_error:
        return jsonify(check_error)

    try:
        user = User.find_by_email(email)
    except Exception as e:
        return jsonify(status="error", errmsg="獲取用戶信息失敗")

    check_error = services.check_password(user, password, user_ip, login_failure_nums)
    
    if check_error:
        return jsonify(check_error)

    response = services.set_login_session(user, password,remember_me)
    
    return response


@auth.route("/session",methods=["GET"])
def check_login():
    """獲取用戶登入狀態 功能"""
    name = session.get(username)
    
    if name is not None:
        flash (u"該用戶已登入")
    else:
        flash(u"該用戶未登入")


@auth.route('/logout')
@login_required
def logout():
    """清除session數據"""
    session.clear()
    logout_user()
    response = make_response('delCookie')
    response.delete_cookie('username')
    return response


@auth.route('/register')
def register():
    return render_template('auth/registration.html')


@auth.route('/register/check',methods=['POST'])
def register_check():
    """用戶註冊功能"""
    print(request.get_data())
    username = request.form.get("username")
    cellphone = request.form.get("cellphone")
    email = request.form.get("email")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    image_code_id = request.form.get("image_code_id")
    image_code = request.form.get("image_code")

    check_failure = services.check_captcha(image_code_id, image_code)

    if check_failure:
        return jsonify(check_failure)

    check_failure = services.check_register_info(cellphone, password, password2, email, username)

    if check_failure:
        return jsonify(check_failure)

    check_failure = services.check_double_register(username, email, cellphone)

    if check_failure:
        return jsonify(check_failure)
    
    result = services.save_register(username, email, cellphone, password)
    print(result)
    return jsonify(result)
    
    
    
@auth.route('/information', methods=["POST","GET"])
@login_required
def information():
    """設置用戶頭像
    參數: 圖片(多媒體表單格式) 用戶id (g.user_id)
    """
    form = UserInfomationForm()

    if form.validate_on_submit():
        current_user.gender = form.gender.data
        current_user.birthday = form.birthday.data
        current_user.user_id = form.user_id.data
        current_user.country = form.country.data
        current_user.address = form.address.data
        current_user.LINE = form.LINE.data

        try:
            db.session.add(current_user)
            db.session.commit()
            flash('實名認證完成')
            return redirect(url_for('auth.my'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash(u"查詢數據庫異常")
            
    return render_template("auth/information.html",form=form)


# @auth.route("/images", methods=["POST","GET"])
# @login_required
# def save_images():
#     form = UploadImageForm()
#     if form.validate_on_submit():
        
#         try:
#             filename = photos.save(form.photo.data)
#             filename ="images/"+ filename
#             # 返回了文件的url路径，而不是文件路径
#             file_url = photos.url(filename)
#             current_user.image_url = filename

#         except Exception as e:
#             current_app.logger.error(e)
#             flash(u"不支持該照片格式")
#             return render_template('auth/images.html', form=form)        

        

#         try:
#             db.session.add(current_user)
#             db.session.commit()
#             flash(u'照片提交完成')
#             return redirect(url_for("auth.my"))

#         except Exception as e:
#             db.session.rollback()
#             current_app.logger.error(e)
#             flash(u"查詢數據庫異常")

#     return render_template('auth/images.html', form=form)
    





@auth.route('/password/reset')
def password_reset():
    return render_template("auth/password_reset.html")

@auth.route('/captcha/check',methods=["POST"])
def captcha_check():
    image_code = request.form.get("image_code")
    image_code_id = request.form.get("image_code_id")
    cellphone = request.form.get("cellphone")
    email = request.form.get("email")
   
    # 校驗參數
    if not all ([image_code_id,image_code]):
        return jsonify(errno=0,errmsg="參數不完整")
        # 從redis中取出真實的圖片驗證碼
    try:
        real_image_code = redis_store.get("image_code_%s"%image_code_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=0,errmsg="Redis數據庫錯誤")
    
    #判斷圖片驗證碼是否過期
    if real_image_code is None:
        #表示圖片驗證碼沒有或者過期
        return jsonify(errno=0,errmsg="圖片驗證碼失效")
    # 刪除redis中的圖片驗證碼，防止用戶使用同一個圖片驗證法驗證多次
    try:
        redis_store.delete("image_code_%s" %image_code_id)
    except Exception as e:
        current_user.logger.error(e)

    # 與用戶填寫的值進行對比
    if str(real_image_code,encoding='utf-8').lower() != image_code.lower():
        # 表示用戶填寫錯誤
        return jsonify(errno=0,errmsg="數據錯誤")
    else:
        u = User.query.filter(and_(User.cellphone==cellphone, User.email==email)).first()
        if u is not None:
            response = make_response(jsonify({'errno':1,'errmsg':'數據查詢成功'}))
            response.set_cookie("email",u.email)
            return response
        else:
            return jsonify(errno=0,errmsg="數據查詢失敗")


@auth.route("/password/check",methods=["POST"])
def password_check():
    password = request.form.get("password")
    password2 = request.form.get ("password2")
    email = request.cookies.get("email")
    if not all([password, password2, email]):
        return jsonify(errno=0,errmsg="參數不完整")
    user = User.query.filter_by(email=email).first()
    from werkzeug.security import generate_password_hash
    if user:
        user.password=password
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(errno=1,errmsg="參數保存成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=0,errmsg="數據庫錯誤")


@auth.route('/my')
def my():
    return render_template("my.html")


@auth.route('/info', methods=["POST"])
@login_required
def update_info():
    username = request.form.get("username")
    cellphone = request.form.get("cellphone")
    u = User.query.filter(User.username==username).first()
    if u:
        return jsonify(error=0,errmsg="該姓名已被註冊過")
    if not re.match(r"^09\d{8}$",cellphone):
        return jsonify(error=0,errmsg="請輸入正確的手機號格式")
    u = User.query.filter(User.id==current_user.id).update({"username":username, "cellphone":cellphone})
    try:
        db.session.commit()
        return jsonify(errno=1,errmsg="參數保存成功")    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=0,errmsg="系統忙碌中，請稍後再試")    
    





# @auth.route('/confirm/<token>')
# @login_required
# def confirm(token):
#     if current_user.confirmed:
#         return redirect(url_for('main.index'))
#     if current_user.confirm(token):
#         flash ('您的郵箱已經進行認證')
#     else:
#         flash('已經失效')
#     return redirect(url_for('main.index'))

# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated \
#         and not current_user.confirmed:
#         return redirect(url_for('auth.unconfirmed'))

# @auth.route('/unconfirmed')
# def unconfirmed():
#     if current_user.is_anonymous or current_user.confirmed:
#         return redirect(url_for('main.index'))
#     return redirect(url_for('auth/unconfirmed.html'))

# @auth.route('/confirm')
# @login_required
# def resend_confirmation():
#     token = current_user.generate_confirmation_token()
#     send_emil(current_user.email, '請確認您的帳戶', 'auth/email/confirm', user=current_user, token=token)
#     flash('已經發送確認郵件')
#     return redirect(url_for('main.index'))
