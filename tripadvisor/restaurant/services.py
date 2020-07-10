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


def save_reservation_check(row):
    order_id = "%s-%s" % (int(round(time.time()*1000)),random.randint(0,99999999))
        
    store = TripAdvisor.find_by_name(row["restaurant"])
    result = Reservation(title_name = row["restaurant"],
                        people = row["people"],
                        booking_date = row["booking_date"],
                        booking_time = row["booking_time"],
                        order_id1 = order_id,
                        user = row["current_user"]._get_current_object(),
                        restaurant_id=store.id)
    return result


def reservation_condition():
    now = datetime.now().strftime("%Y-%m-%d")
    reservations = []
    record = db.session.query(Reservation, TripAdvisor).select_from(TripAdvisor)\
                     .outerjoin(Reservation, and_(Reservation.restaurant_id == TripAdvisor.id, 
                                                Reservation.booking_date>now))\
                     .join(User, and_(Reservation.user_id == User.id, User.id == current_user.id))\
                     .all()

    for r in record:
        row = {}
        row["title"] = r[0].title_name
        row["date"] = r[0].booking_date
        row["booking_time"] = r[0].booking_time
        row["people"] = r[0].people
        row["order_id"] = r[0].order_id1
        row["create_time"] = r[0].create_time.strftime('%Y-%m-%d')
        row["image"] = r[1].info_url.split(",")[0]
        reservations.append(row)
    
    histories = []
    history = db.session.query(Reservation, TripAdvisor).select_from(TripAdvisor).outerjoin(Reservation, and_(Reservation.restaurant_id==TripAdvisor.id,Reservation.booking_date < now)).join(User, and_(Reservation.user_id==User.id, User.id==current_user.id)).order_by(Reservation.booking_date.desc()).all()
    for h in history:
        row["title"] = h[0].title_name
        row["date"] = h[0].booking_date
        row["order_id"] = h[0].order_id1
        row["image"] = h[1].info_url.split(",")[0]
        histories.append(row)
    
    return reservations, histories


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

def reservatin(row):
    result = {}
    restaurant = row["restaurant"]
    people = row["people"]
    booking_date = row["booking_date"]
    booking_time = row["booking_time"]

    if not all ([restaurant, people, booking_date, booking_time]):
        result["errno"] = 0
        result["errmsg"] = "參數不完整"
    else:
        row["order_id"] = "%s-%s" % (int(round(time.time()*1000)), random.randint(0,99999999))
    
    store = TripAdvisor.query.filter_by(title=restaurant).first()
    r = Reservation(title_name = restaurant,
                    people = people,
                    booking_date = booking_date,
                    booking_time = booking_time,
                    order_id1 = order_id,
                    user = current_user._get_current_object(),
                    restaurant_id = store.id)
    try:
        db.session.add(r)
        result["errno"] = 1
        result["errmsg"] = "參數保存成功"
        result["order_id"] = order_id
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        result["errno"] = 0
        result["errmsg"] = "數據庫錯誤"

    return result


def followe_user():
    followers = []
    follower = Follow.query.join(User, User.id==Follow.followed_id)\
                            .filter(User.username==username)\
                            .all()
    current_user_follower =  Follow.query.join(User, User.id==Follow.follower_id)\
                                        .filter(User.id==current_user.id)\
                                        .all()
    current_user_followers=[]

    for a in current_user_follower:
        current_user_followers.append(a.followed.id)

    for f in follower:
        follow_condition = "關注中" if f.follower.id in current_user_followers else "追蹤" if f.follower.id != current_user.id else "自己"
        follower_count = f.follower.followers.count()
        followers.append({"user":f.follower.username,"follow_condition":follow_condition,"follower_count":follower_count,"city":f.follower.city,"about_me":f.follower.about_me})

    return followers

def followed_user(username):
    followeds=[]
    followed = Follow.query.join(User, User.id==Follow.follower_id).filter(User.username==username).all()
    current_user_follower =  Follow.query.join(User, User.id==Follow.follower_id).filter(User.id==current_user.id).all()

    current_user_followers=[]
    for a in current_user_follower:
        current_user_followers.append(a.followed.id)
    
    for f in followed:
        follow_condition = "關注中" if f.followed.id in current_user_followers else "追蹤" if f.followed.id != current_user.id else "自己"
        follower_count = f.followed.followers.count()
        city = f.followed.city if f.followed.city else "城市"
        about_me = f.followed.about_me if f.followed.about_me else "趕快來認識我吧"
        followeds.append({"user":f.followed.username,"follow_condition":follow_condition,"follower_count":follower_count,"city":city,"about_me":about_me})
    
    return followeds


def save_member_info(username, city, about_me, website):
    user = User.query.filter(User.username==username).first()
    user.website = website if website else None
    user.city = city if city else None
    user.about_me = about_me if about_me else None 

    result = {}
    try:
        db.session.commit()
        result["errno"] = 1
        result["errmsg"] = "數據保存成功"

    except Exception as e:
        db.session.rollback()
        result["errno"] = 0
        result["errmsg"] = "數據庫異常"
    
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