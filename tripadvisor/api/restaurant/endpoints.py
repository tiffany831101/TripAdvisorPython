from flask import render_template, current_app, request, jsonify
from flask_login import login_required, current_user

from datetime import datetime
import logging
import json

from tripadvisor import dao, tasks
from tripadvisor.api.restaurant import services, main
from tripadvisor.models import User


logger = logging.getLogger()

@main.route('/restaurant')
def index():
    logger.error("error msg")
    logger.warn("warn msg")
    logger.info("info msg")
    logger.debug("debug msg")
    return render_template('index.html',current_time=datetime.utcnow())


@main.route('/restaurant/list')
def restaurant_list():
    return render_template("restaurant.html")


@main.route('/comment/<restaurant>')
def restaurant(restaurant):
    restaurant, comments = services.get_restaurant_comments(restaurant)
    return render_template("review.html",restaurant=restaurant, comment=comments)


@main.route('/restaurant/<restaurant>',methods=["POST","GET"])
@login_required
def search_result(restaurant):
    restaurant, comments, like, love =  services.get_restaurant_pages(restaurant)
    
    return render_template("res_result.html", data=restaurant, like=like,\
                                                love=love, comment=comments) 


@main.route('/user/<username>')
@login_required
def user(username):
    read = services.recent_read_page()
    comments = services.get_favorit_comments(username)
    user, restaurants, count = services.get_favorit_restaurant(username)

    return render_template('user.html',store_list=restaurants, count=count, comment_list=comments, user=user, read_list=read)


@main.route("/restaurant/filter")
def restaurant_filter():
    page = request.args.get("page")
    page = int(page) if page else 1
    
    redis_key, result = services.get_restaurant_pages_by_page(page)

    if result:
        return result, 200, {"Content-Type":"application/json"}

    result = services.get_restaurant_info_from_mysql_by_page(page)
    result = json.dumps(result)
    services.cache(redis_key,page, result)
    
    return result, 200, {"Content-Type":"application/json"}
    

@main.route('/restaurant/search')
def restaurant_search():
    """獲取餐廳的列表信息(搜索頁面)"""
    data = request.args.to_dict()
    data["page"] = int(data["page"]) if 'page' in data else 1
    data["user"] = current_user.get_id()

    redis_key, result = services.get_restaurant_info_from_redis(**data)

    if result:
        return result, 200, {"Content-Type":"application/json"}
    
    restaurant = services.get_restaurant_info_from_mysql(**data)
    result = services.get_result_list(data, restaurant)
    services.cache(redis_key, data["page"], json.dumps(result))
    return result, 200, {"Content-Type":"application/json"}


@main.route('/read/count/<restaurant>')
def read_count(restaurant):
    submit = services.submit_click(restaurant, current_user)
    result = dao.save(submit)
    return jsonify(result)

