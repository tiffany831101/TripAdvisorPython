from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
import functools

# 定義驗證登入狀態的裝飾器
def login_required(view_func):
    # 內層函數
    @functools.wraps(view_func)
    def wrapper(*args,**kwargs):
        # 判斷用戶的登入狀態
        user_id = session("user_id")
        # 如果用戶是登入的，執行視圖函數
        if user_id is not None:
            # 將user_id保存於g對象中，在視圖函數中可透過g對象獲得保存數據
            g.user_id = user_id
            return view_func(**args, **kwargs)
        else:
            # 如果未登入，返回未登入的信息
            return jsonify(errno="SESSIONERROR", errmsg="用戶未登入")
    return wrapper

@login_required
def set_uset_avatar():
    user_id = g.user_id
    pass

