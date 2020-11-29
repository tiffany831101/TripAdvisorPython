from flask import request, jsonify
from flask_login import login_required, current_user

from tripadvisor import tasks
from tripadvisor.api.user import user, services
from tripadvisor.models import User, Comment

import logging
from urllib.parse import unquote 

logger = logging.getLogger()


@user.route('/restaurant/like', methods = ['POST'])
def like():
    """餐廳收藏功能"""
    res = {'status': False}
    try:
        data = request.form
        restaurant = unquote(data['restaurant'])
        tasks.follow_restaurant(current_user, restaurant)
        return jsonify(res)

    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/restaurant/unlike', methods = ['POST'])
def unlike():
    """取消餐廳收藏功能"""
    res = {'status': False}
    try:
        data = request.form
        restaurant = unquote(data['restaurant'])
        tasks.unfollow_restaurant(current_user.id, restaurant)
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route("/about_me/<username>", methods=['POST'])
@login_required
def about_me(username):
    """更改個人資訊功能"""
    res = {'status': False}
    try:
        data = request.form
        submit = services.update_aboutMe(username, data)
        res.update({'status': True})
        return jsonify(res)

    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/comment/like')
def comment_like():
    """留言按讚功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        submit = tasks.like_comment(data['id'], current_user)
        res.update({'status': True})
        return res

    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/comment/unlike')
def comment_unlike():
    """留言收回讚功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        comment = Comment().find_by_id(data['id'])
        tasks.unlike_comment(current_user.id, comment)
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/comment/edit/<int:id>', methods=["POST"])
def review_edit(id):
    """評論餐廳功能"""
    res = {'status': False}
    try:
        services.submit_comments(id, current_user, request.form)
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/follow')
@login_required
def follow():
    """用戶追蹤功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        user = User().find_by_username(data['username'])
        if user is None:
            res['msg'] = '查無該用戶'
            return jsonify(res)

        if current_user.is_following(user):
            res['msg'] = '您已關注該用戶'
            return jsonify(res)
        else:
            current_user.follow(user)
            res.update({'status': True, 'msg': u"您已成功關注%s" % data['username']})
            return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)
    

@user.route('/unfollow')
@login_required
def unfollow():
    """取消追蹤功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        user = User().find_by_username(data['username'])
        if user is None:
            res['status'] = '查無該用戶'
            return jsonify(res)
        else:
            current_user.unfollow(user)
            res.update({'status': True, 'msg': u'您已成功取消對%s的關注' % data['username']})
            return jsonify(res)

    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/followers')
@login_required
def followers():
    """粉絲名單查詢功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        followers = services.get_followers(data['username'])
        res.update({'status': True, 'data': followers})
        return jsonify(res)

    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/followed')
@login_required
def followed():
    """用戶追蹤名單查詢功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        followed = services.followed_user(data['username'])
        res.update({'status': True, 'data': followed})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/comments')
@login_required
def comments():
    """獲取用戶的評論以及是否按讚功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()

        if 'username' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401

        username = unquote(data['username'])

        comments = services.get_favorit_comments(username)
        res.update({'status': True, 'data': comments})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/user/visited')
@login_required
def visited():
    """獲取五則用戶最近瀏覽頁面的功能"""
    res = {'status': False}
    try:
        pages = services.visted_pages()
        res.update({'status':True, 'data':pages})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@user.route('/user/liked')
@login_required
def liked():
    """查詢用戶按讚餐廳狀況"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        username = unquote(data['username'])
        pages, count = services.query_restaurant(username)
        res.update({'status':True, 'data': pages, 'count': count})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)