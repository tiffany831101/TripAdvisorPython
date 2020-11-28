from flask import render_template, current_app, request, jsonify
from flask_login import login_required, current_user

from datetime import datetime
import logging
from urllib.parse import unquote 

from tripadvisor import dao, tasks
from tripadvisor.api.restaurant import services, main
from tripadvisor.models import User

logger = logging.getLogger()


@main.route('/restaurant/list')
def restaurant_list():
    return render_template('restaurant.html')


@main.route('/comment/<restaurant>')
def restaurant(restaurant):
    return render_template('review.html')


@main.route('/restaurant/<restaurant>',methods=['POST', 'GET'])
@login_required
def search_result(restaurant):
    restaurant, comments, like, love =  services.get_restaurant_pages(restaurant)
    return render_template("res_result.html", data=restaurant, like=like,\
                                                love=love, comment=comments)                                            

@main.route('/user/<username>')
@login_required
def user(username):
    comments = services.get_favorit_comments(username)

    user = User().find_by_username(username)

    return render_template('user.html', comment_list=comments, user=user)


@main.route('/restaurant/filter')
def restaurant_filter():
    """獲取餐廳的列表信息(搜索頁面)"""
    res = {'status': False}
    try:
        page = request.args.get('page')
        page = int(page) if page else 1

        result_dict = services.fuzzy_search(page)
        
        res.update({'status': True})
        res.update(result_dict)
        return res, 200, {'Content-Type': 'application/json'}
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)
    

@main.route('/restaurant/search')
def restaurant_search():
    """根據搜尋條件，獲取餐廳的列表信息"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        data['page'] = int(data['page']) if 'page' in data else 1
        data['user'] = current_user.get_id()
        
        query = services.query(**data)
        result_dict = services.to_dict(data, query)

        res.update({'status': True})
        res.update(result_dict)
        return res, 200, {'Content-Type':'application/json'}
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@main.route('/restaurant/city')
def get_city():
    """獲取餐廳城市功能"""
    res = {'status': False}
    try:
        cities = tasks.get_city()

        res.update({'status':True, 'data': cities})

        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@main.route('/restaurant/area')
def get_area():
    """獲取餐廳地區功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        
        if 'city' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401
        
        data = tasks.get_area(data['city'])
        areas = []
        for area in data:
            areas.append(area)
        
        res.update({'status':True, 'data': areas})

        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@main.route('/restaurant/hito')
def get_top10_restaurant():
    """獲取前十名餐廳功能"""
    res = {'status': False}
    try:
        data = tasks.get_top10_restaurant()
        restaurants = []
        for restaurant in data:
            restaurants.append(restaurant)
        res.update({'status': True, 'data': restaurants})
        return jsonify(res)

    except Exception as e:
        logger.error(e)
        return jsonify(res)


@main.route('/read/count/<restaurant>')
def read_count(restaurant):
    res = {'status': False}
    try:
        submit = services.submit_click(restaurant, current_user)
        dao.save(submit)
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@main.route('/restaurant/comments')
def get_comments():
    """獲取餐廳評論功能"""
    res = {'status': False}
    try:
        data = request.args.to_dict()

        if 'restaurant' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401

        restaurant = unquote(data['restaurant'])
        comments = tasks.get_comments(restaurant)
        res.update({'status': True, 'data': comments})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@main.route('/restaurant/review')
def restaurant_review():
    res = {'status': False}
    try:
        data = request.args.to_dict()
        if 'restaurant' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res), 401
            
        restaurant = unquote(data['restaurant'])
        information, reviews = services.get_restaurant_comments(restaurant)
        res.update({'status': True, 'information': information, 'reviews': reviews})
        return jsonify(res)

    except Exception as e:
        logger.error(e)
        return jsonify(res)