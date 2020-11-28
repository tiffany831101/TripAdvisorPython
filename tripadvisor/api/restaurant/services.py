from flask import current_app
from flask_login import login_required, current_user
import logging

from tripadvisor.models import User, TripAdvisor, Comment,\
                                Comment_like, Click
from tripadvisor import tasks, cache
from tripadvisor.settings.defaults import *

logger = logging.getLogger()

CACHE_TIMEOUT = 60 * 10


def get_userId():
    user_id = current_user.get_id()
    return current_user.id if user_id else 0


def get_favorit_comments(username):
    comment = tasks.author_following_comments(username)
    my_following_comments = tasks.my_following_comments(current_user.id)
                            
    comment_like = [u.id for u in my_following_comments]

    followed_id = [ i.followed_id for i in current_user.followed.all()]

    comments = []
    for c in comment:
        row = {}
        row['follow_condition'] = '關注中' if c.author_id in followed_id else '追蹤' if c.author_id!=current_user.id else "自己"
        row['like_condition'] = '已讚' if c.id in comment_like else '讚'
        row['review_content'] = c.review_content
        row['rating'] = c.rating
        row['author'] = c.author.username
        row['title'] = c.restaurant.title

        comments.append(row)

    return comments


def query(**kwargs):
    user_id = get_userId()

    filter_params = []
    if kwargs['keyword']:
        filter_params.append(TripAdvisor.title.contains(kwargs['keyword']))

    if kwargs['area']:
        filter_params.append(TripAdvisor.area == kwargs['area'])  

    if kwargs['food']:
        filter_params.append(TripAdvisor.res_type.contains(kwargs['food']))    

    if kwargs['filter'] == '評論數':
        restaurant = tasks.comment_search(int(user_id), params=filter_params)

    elif kwargs['filter'] == '評分數':
        restaurant = tasks.rating_search(int(user_id), params=filter_params)
    
    return restaurant


def get_result(restaurant_object):
    items  = restaurant_object.items
    pages  = restaurant_object.pages
    result = []

    if not items:
        return

    for item in items:
        row = {}
        row = item[0].to_dict()
        row['info_url'] = row['info_url'][0]
        row['comment']  = row['comment'][0]
        row['love'] = '已收藏'
        
        if current_user.get_id() and item[1] == current_user.username:
            row['love'] = '已收藏'
        else:
            row['love'] = '收藏'
    
        result.append(row)

    return pages, result


@cache.memoize(CACHE_TIMEOUT)
def to_dict(data, restaurant):
    restaurant_object = restaurant.paginate(page = data['page'], per_page = 30, error_out = False)
    pages, result = get_result(restaurant_object)

    if result:
        result_dict = dict(data = result, total_page = pages, params = data)
        return result_dict


@cache.memoize(CACHE_TIMEOUT)
def fuzzy_search(page):
    user_id = get_userId()
    
    restaurant_object = tasks.page_filter(user_id, page=page)
    pages, result = get_result(restaurant_object)
    
    if not result:
        return
    
    result_dict = dict(data=result, total_page=pages)
    return result_dict


def get_restaurant_comments(name):
    restaurant = TripAdvisor().find_by_name(name)

    if not restaurant:
        return
    
    information = restaurant.to_comment_dict()

    records = Comment().get_comments(restaurant.id)
    
    reviews = [ record.to_dict() for record in records ]
    
    return information, reviews


def submit_click(restaurant, current_user):
    store = TripAdvisor().find_by_name(restaurant)
    if current_user.is_authenticated:
        c = Click(
            store_id = store.id,
            user_id = current_user.id
        )
        store.read_count = store.read_count + 1 
        return c


def get_restaurant_pages(name):
    restaurant = TripAdvisor().find_by_name(name)

    comments = Comment().find_all(restaurant.id)

    likes = Comment_like().find_all(current_user.id)
    
    love = tasks.like_restaurant(restaurant.id, current_user.id)

    restaurant = restaurant.to_dict()
    return restaurant, comments, likes, love
