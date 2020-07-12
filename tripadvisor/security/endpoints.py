from flask import render_template, redirect, request, flash, make_response, jsonify, session
from flask_login import login_required, current_user, logout_user
import logging

from tripadvisor.security import auth, services
from tripadvisor.email import send_message

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


@auth.route('/login',methods=["POST"])
def login():
    """登入功能"""
    data = request.form
    user_ip = request.remote_addr

    if not all ([data["email"], data["password"]]):
        return jsonify(status="error", errmsg="參數不完整")
    
    is_error = services.check_parmas(data, user_ip)    
    if is_error:
        return jsonify(is_error)

    response = services.set_login_session(data)
    return response


@auth.route('/register/check',methods=['POST'])
def register_check():
    """用戶註冊功能"""
    data = request.form.to_dict()

    if not all ([data["username"], data["cellphone"],data["email"], data["password"], data["password2"], data["image_code_id"], data["image_code"]]):
        return jsonify(status="error", errmsg="參數不完整")

    result = services.user_register(**data)
    
    return jsonify(result)
    

@auth.route('/captcha/check',methods=["POST"])
def captcha_check():
    data = request.form.to_dict()

    if not all ([data["cellphone"], data["email"], data["image_code_id"], data["image_code"]]):
        return jsonify(status="error", errmsg="參數不完整")

    user = services.verify_info(data)
       
    if user:
        response = make_response(jsonify(status = "success", msg= "數據查詢成功"))
        response.set_cookie("email", user.email)
        return response
    
    else:
        return jsonify(status="error",errmsg="請輸入正確Email")
    

@auth.route("/password/check",methods=["POST"])
def password_check():
    data = request.form.to_dict()

    if not all ([data["email"], data["password"], data["password2"]]):
        return jsonify(status="error", errmsg="參數不完整")

    result = services.update_password(data)
    
    return jsonify(result)


@auth.route('/info', methods=["POST"])
@login_required
def update_info():
    data = request.form.to_dict()
    
    result = services.update_info(data, current_user)
    
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
