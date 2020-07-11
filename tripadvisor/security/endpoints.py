from flask import render_template, redirect, request, url_for, flash, make_response, jsonify, session, current_app
from flask_login import login_required, current_user, logout_user

import logging

from tripadvisor.security import auth, services
from tripadvisor.models import User
from tripadvisor.email import send_message
from tripadvisor.security.forms import UserInfomationForm
from tripadvisor import db, photos, CSRFProtect, dao
from tripadvisor.settings.defaults import *


logger = logging.getLogger()


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login/html',methods=["POST","GET"])
def login_html():
    return render_template('auth/login.html')


@auth.route('/register')
def register():
    return render_template('auth/registration.html')


@auth.route('/password/reset')
def password_reset():
    return render_template("auth/password_reset.html")


@auth.route('/my')
def my():
    return render_template("my.html")


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
    """獲取用戶登入狀態"""
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


@auth.route('/register/check',methods=['POST'])
def register_check():
    """用戶註冊功能"""
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
    
    check_failure = services.check_register_info(**{"cellphone":cellphone, "email":email})

    if check_failure:
        return jsonify(check_failure)

    check_failure = services.check_double_register(**{"username":username, "email":email, "cellphone":cellphone})

    if check_failure:
        return jsonify(check_failure)
    
    user = User(username=username, email=email, cellphone=cellphone, password =password)
    result = dao.save(user)
    return jsonify(result)
    

@auth.route('/captcha/check',methods=["POST"])
def captcha_check():
    email = request.form.get("email")
    cellphone = request.form.get("cellphone")
    image_code = request.form.get("image_code")
    image_code_id = request.form.get("image_code_id")

    check_failure = services.check_captcha(image_code_id, image_code)

    if check_failure:
        return jsonify(check_failure)
   
    user = User.find_by_cellphone_and_email(cellphone, email)
    
    if user:
        response = make_response(jsonify(status = "success", msg= "數據查詢成功"))
        response.set_cookie("email", user.email)
        return response
    else:
        return jsonify(status="error",errmsg="請輸入正確Email")
    

@auth.route("/password/check",methods=["POST"])
def password_check():
    email = request.cookies.get("email")
    password = request.form.get("password")
    password2 = request.form.get ("password2")

    if not email:
        return jsonify(status="error",errmsg="內部系統繁忙中，請再試一次")
    
    user = User.find_by_email(email)

    if user:
        user.password = password
    
    result = dao.save(user)
    
    return jsonify(result)


@auth.route('/info', methods=["POST"])
@login_required
def update_info():
    username = request.form.get("username")
    cellphone = request.form.get("cellphone")
    
    check_error = services.check_double_register(username=username)
    if check_error:
        return jsonify(check_error)
    
    check_failure = services.check_register_info(**{"cellphone":cellphone})

    if check_failure:
        return jsonify(check_failure)
    
    result = User.update(current_user.id, **{"username":username, "cellphone":cellphone})
    
    return jsonify(result)   


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
