from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash, current_app, request, jsonify
import json
from . import main
from .forms import QueryForm, EditionProfileForm, PostForm, BookingForm
from .. import db
from ..models import User, Role, Post, Survey, Food, TripAdvisor, Reservation, Comment, Love
from flask_login import login_required, current_user
import logging
from flask import current_app #全局上下文
from app import constants
import time
import random
from sqlalchemy import and_
@main.route('/resturant')
def index():
    current_app.logger.error("error msg")
    current_app.logger.warn("warn msg")
    current_app.logger.info("info msg")
    current_app.logger.debug("debug msg")
    return render_template('index.html',current_time=datetime.utcnow())

@main.route('/query',methods=['GET','POST'])
@login_required
def query():
    form = QueryForm()
    if form.validate_on_submit():
        s = Survey(
            date = form.date.data.strftime('%Y-%m-%d'),
            price = form.price.data,
            satisfication =form.satisfication.data,
            opinion = form.opinion.data,
            intention =form.intention.data,
            survey = current_user._get_current_object())
        try:
            db.session.add(s)
            
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash(u"查詢數據庫異常")

        food_ids = form.food.data
        
        if food_ids:
            foods = Food.query.filter(Food.id.in_(food_ids)).all()
            print(foods)
            if foods:
                s.foods = foods
                try:
                    db.session.add(s)
                    db.session.commit()
                    flash(u'您寶貴的意見，是我們成長的動力')
                    return redirect(url_for('auth.my'))
                except Exception as e:
                    current_app.logger.error(e)
                    flash(u"數據庫查詢異常")
            
    return render_template('query.html',form=form)




@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter(User.id==current_user.id).first()
    count = user.restaurant_love.count() 
    data = user.restaurant_love.all()
    
    return render_template('user.html',data=data,count=count)

@main.route('/forum',methods=['GET','POST'])
def forum():
    form=PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
        author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.forum'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page',1,type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=5,error_out=False)
    posts = pagination.items
    return render_template('forum.html', form=form, posts=posts, pagination=pagination)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',post=[post])



@main.route('/follow/<username>')
@login_required
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u'無效的用戶')
        return redirect(url_for('.forum'))
    if current_user.is_following(user):
        flash(u'您已關注%s'%username)
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'你已成功關注%s' % username)
    return redirect(url_for('.forum'))

@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'無效的用戶')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'您已取消關注%s' % username)
    return redirect(url_for('.forum'))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'無效的用戶')
        return redirect(url_for('.forum'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(
        page,10,error_out=False)
    follows = [{'user':item.follower, 'timestamp':item.timestamp}
    for item in pagination.items]
    return render_template('followers.html',user=user,title='Followers of',
    endpoint='.followers', pagination=pagination, follows=follows)

@main.route('/followed/<username>')
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'該用戶不存在')
        return redirect(url_for('.forum'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(
        page,10,error_out=False)
    followed = [{'user':item.followed, 'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followed.html', user=user, title='Followed of', endpoint='.followed',
    pagination=pagination, follows=follows)


@main.route('/comment',methods=["POST","GET"])
def get_comment_list():
    return render_template("comment.html")


@main.route('/comment/result')
def result_get():
    dict = request.values.to_dict()
    if dict.get("data") == "new":
        survey = Survey.query.order_by(Survey.create_time.desc()).all()
    elif dict.get("data") == "high":
        survey = Survey.query.order_by(Survey.satisfication.desc()).all()
    else:
        survey = Survey.query.order_by(Survey.satisfication.asc()).all()
    list=[]
    for s in survey:
        author = s.survey.username
        opinion = s.opinion
        time = s.create_time.strftime('%Y-%m-%d')
        star= s.satisfication
        comment={
            "author":author,
            "opinion":opinion,
            "star":star,
            "time":time            }
        list.append(comment)
    return jsonify(errno=0,data={"list":list})



@main.route('/reservation/<restaurant>',methods=["POST","GET"])
@login_required
def reservation(restaurant):
    data = TripAdvisor.query.filter_by(title=restaurant).first()
    if not data:
        return render_template("booking.html")
    return render_template("booking.html",data=data)

@main.route('/reservation/check',methods=["POST"])
def reservation_check():
    restaurant = request.form.get("restaurant")
    people = request.form.get("people")
    booking_date = request.form.get("booking_date")
    booking_time = request.form.get("booking_time")
    
    if not all ([restaurant,people,booking_date,booking_time]):
        return jsonify(errno=0,errmsg="參數不完整")
    else:
        order_id = "%s-%s" % (int(round(time.time()*1000)),random.randint(0,99999999))
        print(order_id)
    r = Reservation(title_name=restaurant,
                    people=people,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    order_id1=order_id,
                    user=current_user._get_current_object())
    try:
        db.session.add(r)
        return jsonify(errno=1,errmsg="參數保存成功",order_id=order_id)
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=0,errmsg="數據庫錯誤")

@main.route('/reservation/result')
@login_required
def result():
    now = time.strftime("%Y-%m-%d", time.localtime())
    reservation = Reservation.query.filter(and_(Reservation.userid==current_user.id,Reservation.booking_date>now)).order_by(Reservation.booking_date.desc()).all()
    history = Reservation.query.filter(and_(Reservation.userid==current_user.id,Reservation.booking_date<now)).order_by(Reservation.booking_date.desc()).all()

    
    return render_template("result.html", reservation=reservation, history=history)

@main.route('/reservation/revise/<order_id>',methods=["POST","GET"])
def order_revise(order_id):
    data = Reservation.query.filter_by(order_id1=order_id).first()
    return render_template("revise.html", data=data)
@main.route('/reservation/order/cancel/<order_id>',methods=["POST"])
def order_cancel(order_id):
    
    r = Reservation.query.filter_by(order_id1=order_id).first()
    if r :
        try:
            db.session.delete(r)
            return jsonify(errno=1,ennmsg="參數刪除成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=0,errmsg="數據庫錯誤")

@main.route('/reservation/cancel',methods=["POST"])
def order_confirm_revise():
    order_id = request.form.get("order_id")
    restaurant = request.form.get("restaurant")
    people = request.form.get("people")
    booking_date = request.form.get("booking_date")
    booking_time = request.form.get("booking_time")
    if not all ([order_id,restaurant,people,booking_date,booking_time]):
        return jsonify(errno=0,errmsg="參數不完整")
    r = Reservation.query.filter_by(order_id1=order_id).update({"people":people,"booking_date":booking_date,"booking_time":booking_time})
    
    try:
        db.session.commit()
        return jsonify(errno=1,errmsg="參數保存成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(errno=0,errmsg="數據庫錯誤")




@main.route('/restaurant/list')
def restaurant_list():
    return render_template("restaurant.html")

@main.route('/restaurant/search')
def restaurant_search():
    """獲取餐廳的列表信息(搜索頁面)"""
    address = request.args.get("area") #區域
    res_type = request.args.get("food") #餐廳類型
    sort_key = request.args.get("filter") #過濾類型
    page = request.args.get("page")

    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    filter_params=[]
    if address:
        filter_params.append(TripAdvisor.address==address)
        
    if res_type:
        filter_params.append(TripAdvisor.res_type == res_type)
    
    if sort_key =="評論數":
        restaurant = TripAdvisor.query.filter(*filter_params).order_by(TripAdvisor.rating_count.desc())
    elif sort_key =="評分數":    
        restaurant = TripAdvisor.query.filter(*filter_params).order_by(TripAdvisor.rating.desc())

    restaurant_obj = restaurant.paginate(page=page,per_page=30,error_out= False)
    restaurant_li =restaurant_obj.items
    total_page = restaurant_obj.pages
    restaurant=[]
    for restaurants in restaurant_li:
        restaurant.append(restaurants.to_basic_dict())    

    return jsonify(errno=0,data={"restaurant":restaurant},total_page=total_page)
    


@main.route('/restaurant/<restaurant>',methods=["POST","GET"])
@login_required
def search_result(restaurant):
    data = TripAdvisor.query.filter_by(title=restaurant).first()  
    l = Love.query.filter(and_(Love.storeid==data.id,Love.user_id==current_user.id)).first()
    data = data.to_basic_dict()
    if l:
        return render_template("res_result.html",data=data,l=l)
    else:
        return render_template("res_result.html",data=data)

@main.route('/comment/<restaurant>')
def restaurant(restaurant):
    data = TripAdvisor.query.filter_by(title=restaurant).first()
    data = data.to_basic_dict()
    return render_template("review.html",data=data)

@main.route('/comment/edit/<int:id>',methods=["POST"])
def review_edit(id):
    restaurant =TripAdvisor.query.get_or_404(id)
    rating = request.form.get("rating")
    review_title = request.form.get("review_title")
    review_content = request.form.get("review_content")
    friend = request.form.get("type")
    booking_date = request.form.get("booking_date")
    takeout = request.form.get("takeout")
    vegetable = request.form.get("vegetable")
    service = request.form.get("service")
    disabled = request.form.get("disabled")
    star1 = request.form.get("star1")
    star2 = request.form.get("star2")
    star3 = request.form.get("star3")
    recommend_dish = request.form.get("recommend_dish")
    c =Comment(rating=rating,review_title=review_title,review_content=review_content,friend=friend,booking_date=booking_date,
                    takeout=takeout,vegetable=vegetable,service=service,disabled=disabled,star1=star1,star2=star2,star3=star3,
                    recommend_dish=recommend_dish,
                    author=current_user._get_current_object(),
                    restaurant=restaurant)
    try:
        db.session.add(c)
        db.session.commit()
        return jsonify(errno=1,errmsg="參數保存成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=0,errmsg="數據庫錯誤")


@main.route('/restaurant/like/<id>')
def like(id):
    restaurant =TripAdvisor.query.get_or_404(id)
    focus = request.args.get("like")
    l = Love(focus=focus,author=current_user._get_current_object(),store=restaurant)
    try:
        db.session.add(l)
        db.session.commit()
        return jsonify(errno=1,errmsg="參數保存成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=0,errmsg="數據庫錯誤")

@main.route('/restaurant/unlike/<id>')
def unlike(id):
    restaurant =TripAdvisor.query.get_or_404(id)
    user = User.query.filter(User.id==current_user.id).first()
    a = user.restaurant_love.filter(TripAdvisor.id==restaurant.id).first()
    try:
        db.session.delete(a)
        db.session.commit()
        return jsonify(errno=1,ennmsg="參數刪除成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=0,errmsg="數據庫錯誤")
