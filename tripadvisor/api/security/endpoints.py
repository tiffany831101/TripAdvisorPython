from flask import render_template, request, Response, \
                 make_response, jsonify, session 
from flask_login import login_required, current_user, logout_user
from flask_cors import cross_origin
import logging

from tripadvisor.api.security import auth, services
from tripadvisor.email import send_message

logger = logging.getLogger()


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login/html', methods=['GET'])
def login_html():
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET'])
def register():
    return render_template('auth/registration.html')


@auth.route('/password/reset', methods=['GET'])
def password_reset():
    return render_template('auth/password_reset.html')


@auth.route('/member/home')
def home():
    return render_template('my.html')


@auth.route('/logout')
@login_required
def logout():
    """清除session數據"""
    session.clear()
    logout_user()
    response = Response('delCookie')
    response.set_cookie(key='username', value='', expires=0)
    return response


@auth.route('/login', methods=['POST'])
def login():
    """用戶登入功能"""
    res = {'status':False}
    try:
        data = request.form
        user_ip = request.remote_addr

        if 'email' not in data or 'password' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401
                
        is_error = services.check_parmas(data, user_ip)    
        if is_error:
            res.update({'msg': is_error})
            return jsonify(res)

        services.set_login_session(data)
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@auth.route('/register/check',methods=['POST'])
def register_check():
    """用戶註冊功能"""
    res = {'status': False}
    try:
        data = request.form.to_dict()

        if 'username' not in data or 'cellphone' not in data or 'email' not in data or\
            'password' not in data or 'password2' not in data or 'image_code_id' not in data or 'image_code' not in data:
            
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401

        isFailure = services.user_register(**data)

        if isFailure:
            res.update({'msg': isFailure})
            return jsonify(res)
        
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)
    

@auth.route('/captcha/check', methods=['POST'])
def captcha_check():
    """會員認證功能"""
    res = {'status': False}
    try:
        data = request.form

        if 'cellphone' not in data or 'email' not in data \
                or 'image_code_id' not in data or 'image_code' not in data:
                
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401

        isFailure, user = services.verification(data)

        if isFailure:
            res.update({'msg': isFailure})
            return jsonify(res)

        if user:
            res.update({'status': True})
            return jsonify(res)
        else:
            res['msg'] = '查無該用戶，請再次確認手機號碼與Email。'
            return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@auth.route('/password/check', methods=['POST'])
def password_check():
    """修改密碼功能"""
    res = {'status': False}
    try:
        data = request.form

        if 'password' not in data or 'password2' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401
            
        isFailure = services.update_password(data)
        
        if isFailure:
            res['msg'] = isFailure
            return jsonify(res)

        res.update({'status': True})
        return jsonify(res)

    except Exception as e:
        logger.error(e)
        return jsonify(res)


@auth.route('/info', methods=['POST'])
@login_required
def update_info():
    """更改用戶訊息"""
    res = {'status': False}
    try:
        data = request.form
    
        isFailure = services.update_info(data, current_user)
        if isFailure:
            res['msg'] = isFailure
            return jsonify(res)

        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)
