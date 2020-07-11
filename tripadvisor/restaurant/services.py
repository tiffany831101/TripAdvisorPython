from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import and_, func
import logging
import time
import random

from tripadvisor.models import User, Post, Survey, TripAdvisor, Reservation,\
                               Comment, Love, Comment_like,Follow, Click
from tripadvisor import redis_store, db


logger = logging.getLogger()


def favorit_restaurant_count(username):
    if username is not current_user.username:
        user = User.query.filter_by(username = username).first()
        if not user:
            return jsonify(status="error", msg="查無該用戶")
        restaurant = TripAdvisor.query.join(Love, Love.store_id == TripAdvisor.id)\
                                      .filter(Love.user_id == user.id).all()
        count = TripAdvisor.query.join(Love, Love.store_id == TripAdvisor.id)\
                                      .filter(Love.user_id == user.id).count()

    else:
        restaurant = TripAdvisor.query.join(Love, Love.store_id == TripAdvisor.id)\
                                      .filter(Love.user_id == current_user.id).all()

        count = TripAdvisor.query.join(Love, Love.store_id == TripAdvisor.id)\
                                      .filter(Love.user_id == current_user.id).count()
    
    stores=[ r.to_dict() for r in restaurant ]

    return user, stores, count


def favorit_comments(username):
    comment = Comment.query.join(Comment_like, Comment_like.comment_id == Comment.id)\
                           .join(User,and_(Comment_like.user_id == User.id,
                                            User.username==username)).all()
                            
    user_comment = Comment_like.query.filter(Comment_like.user_id==current_user.id).all()

    user_comment_like=[]
    for u in user_comment:
        user_comment_like.append(u.id)
    
    followed_id = [ i.followed_id for i in current_user.followed.all()]

    comments = []
    for c in comment:
        row = {}
        row["follow_condition"] = "關注中" if c.author_id in followed_id else "追蹤" if c.author_id!=current_user.id else "自己"
        row["like_condition"] = "已讚" if c.id in user_comment_like else "讚"
        row["review_content"] = c.review_content
        row["rating"] = c.rating
        row["author"] = c.author.username
        row["title"] = c.restaurant.title

        comments.append(row)

    return comments


def recent_read_page(username):
    recent_read = TripAdvisor.query.join(Click, Click.store_id == TripAdvisor.id)\
                                 .join(User, and_(User.id == Click.user_id,
                                                  User.id==current_user.id))\
                                 .distinct()\
                                 .order_by(Click.create_time.desc())\
                                 .limit(5)
    read = []
    for r in recent_read:
        row = {}
        row["title"] = r.title
        row["picture"] = r.info_url.split(",")[0]
        row["address"] = r.address
        read.append(row)
    return read


def comment_result(survey):
    result =[]
    for s in survey:
        row = {}
        row["author"] = s.survey.username
        row["opinion"] = s.opinion
        row["time"] = s.create_time.strftime('%Y-%m-%d')
        row["star"] = s.satisfication
        result.append(row)
    return result


def get_redis_key(address, res_type, sort_key, page, keyword, user):
    return "restaurant_%s_%s_%s_%s_%s_%s" % (address, res_type, sort_key, page, keyword, user)


def get_restaurant_info_from_redis(address, res_type, sort_key, page, keyword, user):
    redis_key = get_redis_key(address, res_type, sort_key, page, keyword, user)
    try:
        result = redis_store.hget(redis_key, page)
    except Exception as e:
        logger.error(e)
    
    return result


def get_restaurant_info_from_mysql(address, res_type, sort_key, page, keyword, user):
    filter_params=[]
    if keyword:
        filter_params.append(TripAdvisor.title.contains(keyword))
    if address:
        filter_params.append(TripAdvisor.address==address)  
    if res_type:
        filter_params.append(TripAdvisor.res_type.contains(res_type))    

    if sort_key =="評論數":
        if user is not None:
            restaurant = User.comment_search(val=int(current_user.id), params=filter_params)
        else:
            restaurant = User.comment_search(val= int(0), params=filter_params)

    elif sort_key =="評分數":
        if user is not None:
            restaurant = User.rating_search(val=int(current_user.id), params=filter_params)
        else:
            restaurant = User.rating_search(val=int(0), params=filter_params)

    return restaurant