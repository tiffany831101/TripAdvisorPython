from flask import current_app
from flask_login import login_required, current_user
import logging

from tripadvisor.models import User, TripAdvisor,Comment,\
                                Love, Comment_like, Click
from tripadvisor import redis_store, tasks
from tripadvisor.settings.defaults import *

logger = logging.getLogger()


def get_redis_key(address, res_type, sort_key, page, keyword, user):
    return f"restaurant_{address}_{res_type}_{sort_key}_{page}_{keyword}_{user}" 


def get_favorit_restaurant(username):
    user = User()
    if username is not current_user.username:
        user = user.find_by_username(username)
        if not user:
            return {"status":"error", "msg":"查無該用戶"}
        
    restaurant, count = tasks.following_restaurant(user.id)
    
    restaurants = [ r.to_dict() for r in restaurant ]

    return user, restaurants, count


def get_favorit_comments(username):
    comment = tasks.author_following_comments(username)
    my_following_comments = tasks.my_following_comments(current_user.id)
                            
    comment_like=[]
    for u in my_following_comments:
        comment_like.append(u.id)
    
    followed_id = [ i.followed_id for i in current_user.followed.all()]

    comments = []
    for c in comment:
        row = {}
        row["follow_condition"] = "關注中" if c.author_id in followed_id else "追蹤" if c.author_id!=current_user.id else "自己"
        row["like_condition"] = "已讚" if c.id in comment_like else "讚"
        row["review_content"] = c.review_content
        row["rating"] = c.rating
        row["author"] = c.author.username
        row["title"] = c.restaurant.title

        comments.append(row)

    return comments


def recent_read_page():
    user_id = current_user.id
    recent_read = tasks.get_recent_read(user_id)
    read = []
    for r in recent_read:
        row = {}
        row = r.to_dict()
        row["image"] = row["info_url"][3]
        read.append(row)
    
    return read


def get_restaurant_info_from_redis(**kwargs):
    redis_key = get_redis_key(kwargs["area"], kwargs["food"], kwargs["filter"], \
                                kwargs["page"], kwargs["keyword"], kwargs["user"])
    try:
        result = redis_store.hget(redis_key, kwargs["page"])
    except Exception as e:
        logger.error(e)
    return redis_key, result


def get_restaurant_info_from_mysql(**kwargs):
    if not kwargs["user"]:
        user_id = 1
    else:
        user_id = current_user.id
    
    filter_params = []
    if kwargs["keyword"]:
        filter_params.append(TripAdvisor.title.contains(kwargs["keyword"]))

    if kwargs["area"]:
        filter_params.append(TripAdvisor.address==kwargs["area"])  

    if kwargs["food"]:
        filter_params.append(TripAdvisor.res_type.contains(kwargs["food"]))    

    if kwargs["filter"] =="評論數":
        restaurant = tasks.comment_search(int(user_id), params=filter_params)

    elif kwargs["filter"] =="評分數":
        restaurant = tasks.rating_search(int(user_id), params=filter_params)
        
    return restaurant


def to_result_dict(restaurant_object):
    items = restaurant_object.items
    pages = restaurant_object.pages
    if not items:
        return {"status":"error", "errmsg":"參數錯誤"}

    result = []
    for i in items:
        row = {}
        row = i[0].to_dict()
        row["info_url"] = row["info_url"][0]
        row["comment"] = row["comment"][0]
        row["love"] = "已收藏"
        if current_user.get_id() and i[1]==current_user.username:
            row["love"] = "已收藏"
        else:
            row["love"] = "收藏"
    
        result.append(row)

    return pages, result


def get_result_list(data, restaurant):
    restaurant_object = restaurant.paginate(page=data["page"], per_page=30, error_out=False)
    pages, result = to_result_dict(restaurant_object)
    result_dict = dict(errno=1,data=result, total_page=pages, params=data)

    return result_dict


def get_restaurant_info_from_mysql_by_page(page):
    user = current_user.get_id()
    user_id = current_user.id if user else 0
    restaurant_object = tasks.page_filter(user_id, page=page)

    pages, result = to_result_dict(restaurant_object)
    result_dict = dict(errno=1, data=result, total_page=pages)
    return result_dict


def cache(redis_key, page, data):
    try:
        pipeline = redis_store.pipeline()
        pipeline.multi()
        pipeline.hset(redis_key, page, data)
        pipeline.expire(redis_key, RESTAURANT_LIST_PAGE)
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)


def get_restaurant_comments(name):
    restaurant = TripAdvisor()
    restaurant = restaurant.find_by_name(name)

    brief_info = restaurant.to_comment_dict()
    
    comment = Comment()
    comments = comment.get_comments(restaurant.id)

    restaurant_comments = []
    for c in comments:
        restaurant_comments.append(c.to_dict())
    
    return brief_info, restaurant_comments


def submit_click(restaurant, current_user):
    tripadvisor = TripAdvisor()
    store = tripadvisor.find_by_name(restaurant)
    if current_user.is_authenticated:
        c = Click()
        c.store_id = store.id
        c.user_id = current_user.id

        store.read_count = store.read_count + 1 
        return c


def get_restaurant_pages(name):
    tripAdvisor = TripAdvisor()
    restaurant = tripAdvisor.find_by_name(name)

    comment = Comment()
    comments = comment.find_all(restaurant.id)

    comment_like = Comment_like()
    likes = comment_like.find_all(current_user.id)

    love = Love()
    love = love.find_by_store_and_user(restaurant.id, current_user.id)

    restaurant = restaurant.to_dict()
    return restaurant, comments, likes, love


def get_restaurant_pages_by_page(page):
    redis_key = "restaurant_%s" % (page)
    try:
        result = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    return redis_key, result
