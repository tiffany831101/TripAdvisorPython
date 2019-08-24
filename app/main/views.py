from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash, current_app, request, jsonify
import json
from . import main
from .forms import QueryForm, EditionProfileForm, PostForm, BookingForm
from .. import db
from ..models import User, Role, Post, Survey, Food, TripAdvisor, Reservation, Comment, Love, Comment_like,Follow, Click
from flask_login import login_required, current_user
import logging
from flask import current_app #全局上下文
from app import constants
import time
import random
from sqlalchemy import and_,func
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
    if username is not current_user.username:
        user = User.query.filter_by(username=username).first()
        restaurant = TripAdvisor.query.join(Love, Love.store_id==TripAdvisor.id).filter(Love.user_id==user.id).all()
        count= TripAdvisor.query.join(Love, Love.store_id==TripAdvisor.id).filter(Love.user_id==user.id).count()
    else:
        restaurant = TripAdvisor.query.join(Love, Love.store_id==TripAdvisor.id).filter(Love.user_id==current_user.id).all()
        count= TripAdvisor.query.join(Love, Love.store_id==TripAdvisor.id).filter(Love.user_id==current_user.id).count()
    
    store_list=[]
    for r in restaurant:
        store_list.append(r.to_basic_dict())
    
    
    # 收藏評論
    comment = Comment.query.join(Comment_like, Comment_like.comment_id==Comment.id).join(User,and_(Comment_like.user_id==User.id,User.username==username)).all()
    # 最近瀏覽數
    recent_read = TripAdvisor.query.join(Click, Click.store_id== TripAdvisor.id).join(User, and_(User.id==Click.user_id,User.id==current_user.id)).distinct().limit(5)
    read_list=[]
    for r in recent_read:
        title = r.title
        picture = r.info_url.split(",")[0]
        address = r.address
        read_list.append({"picture":picture,"address":address,"picture":picture,"title":title})

    return render_template('user.html',store_list=store_list,count=count,comment=comment,user=user, read_list=read_list)

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
        return jsonify(errno=0,errmsg="查無該用戶")
    if current_user.is_following(user):
        return jsonify(errno=0,errmsg="已關注該用戶")    
    current_user.follow(user)
    return jsonify(errno=1,errmsg=u"您已成功關注%s"%username)


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify(errno=0,errmsg="該用戶不存在")
    current_user.unfollow(user)
    return jsonify(errno=1,errmsg=u"您已取消追蹤%s"%username)

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
    return render_template("test.html")

@main.route("/restaurant/filter")
def restaurant_filter():
    page = request.args.get("page")
    if not page:
        page=int(1)
    user = current_user.get_id()
    if user is not None:
        data = User.page_load(val=int(current_user.id),page=page)
    else:
        data = User.page_load(val=int(0),page=page)
    
    total_page = data.pages
    data = data.items
    data_list=[]
    for d in data:
        title= d[0].title
        res_type=d[0].res_type
        rating_count=d[0].rating_count
        info_url=(d[0].info_url).split(",")[0]
        cellphone=d[0].cellphone
        street = d[0].street
        rating = d[0].rating
        comment= (d[0].comment).split(",")[1]
        count = d[0].read_count
        love = "已收藏" if current_user.get_id() is not None and d[1]==current_user.username else "收藏"
        data_list.append({"title":title, "res_type":res_type, "rating_count":rating_count, "info_url":info_url,"cellphone":cellphone,"street":street,"rating":rating,"comment":comment,"count":count,"love":love})
    return jsonify(errno=1,data=data_list,total_page=total_page)

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
        page = int(1)
    params = {"area":address, "food":res_type, "filter":sort_key}

    filter_params=[]

    if address:
        filter_params.append(TripAdvisor.address==address)  
    if res_type:
        filter_params.append(TripAdvisor.res_type == res_type)
    
    user = current_user.get_id()

    if sort_key =="評論數":
        if user is not None:
            restaurant = user.comment_search(val=int(current_user.id), params=filter_params)
        else:
            restaurant = User.comment_search(val= int(0), params=filter_params)

    elif sort_key =="評分數":
        if user is not None:
            restaurant = user.rating_search(val=int(current_user.id), params=filter_params)
        else:
            restaurant = User.rating_search(val=int(0), params=filter_params)

    restaurant_obj = restaurant.paginate(page=page,per_page=30,error_out= False)
    restaurant_li =restaurant_obj.items
    total_page = restaurant_obj.pages
    
    data_list=[]
    for d in restaurant_li:
        title = d[0].title
        res_type = d[0].res_type
        rating_count = d[0].rating_count
        info_url=(d[0].info_url).split(",")[0]
        cellphone=d[0].cellphone
        street = d[0].street
        rating = d[0].rating
        count = d[0].read_count
        comment= (d[0].comment).split(",")[0]
        love = "已收藏" if current_user.get_id() is not None and d[1]==current_user.username else "收藏"
        data_list.append({"title":title, "res_type":res_type, "rating_count":rating_count, "info_url":info_url,"cellphone":cellphone,"street":street,"rating":rating,"comment":comment,"count":count,"love":love})  
    return jsonify(errno=1,data=data_list,total_page=total_page, params=params)
    


@main.route('/restaurant/<restaurant>',methods=["POST","GET"])
@login_required
def search_result(restaurant):
    data = TripAdvisor.query.filter_by(title=restaurant).first()
    comment = Comment.query.filter(Comment.store_id==data.id).all()
    like = Comment_like.query.filter(Comment_like.user_id==current_user.id).all()
    love = Love.query.filter(and_(Love.store_id==data.id,Love.user_id==current_user.id)).first()
    data = data.to_basic_dict()
    return render_template("res_result.html",data=data,like=like,love=love, comment=comment) 

@main.route('/read/count/<restaurant>')
def read_count(restaurant):
    store = TripAdvisor.query.filter(TripAdvisor.title==restaurant).first()
    if current_user.is_authenticated:
        c = Click(store_id=store.id, user_id=current_user.id)
        try:
            db.session.add(c)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=0,errmsg="數據庫異常")
    # 修改數據 (update??)
    store.read_count = store.read_count + 1 
    try:
        db.session.commit()
        return jsonify(errno=1,errmsg="數據保存成功")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=0,errmsg="數據庫異常")


@main.route('/comment/<restaurant>')
def restaurant(restaurant):
    data = TripAdvisor.query.filter_by(title=restaurant).first()
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


@main.route('/restaurant/like/<restaurant>')
def like(restaurant):
    restaurant =TripAdvisor.query.filter(TripAdvisor.title==restaurant).first()
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

@main.route('/restaurant/unlike/<restaurant>')
def unlike(restaurant):
    restaurant =TripAdvisor.query.filter(TripAdvisor.title==restaurant).first()
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

@main.route("/comment/like/<id>")
def comment_like(id):
    comment = Comment.query.get_or_404(id)
    l = Comment_like(comment_id=comment.id,user_id=current_user.id)
    try:
        db.session.add(l)
        db.session.commit()
        return jsonify(errno=1,errmsg="參數保存成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=0,errmsg="數據庫錯誤")


@main.route("/comment/unlike/<int:id>")
def comment_unlike(id):
    comment=Comment.query.get_or_404(id)
    user = User.query.filter(User.id==current_user.id).first()
    l = user.comment_like.filter(Comment.id==comment.id).first()
    try:
        db.session.delete(l)
        db.session.commit()
        return jsonify(errno=1,ennmsg="參數刪除成功")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=0,errmsg="數據庫錯誤")

@main.route("/followers/<username>")
@login_required
def follow_user(username):
    follower_list=[]
    follower = Follow.query.join(User, User.id==Follow.followed_id).filter(User.username==username).all()    
    for f in follower:
        follower_list.append({"user":f.follower.username})
    return jsonify(errno=1,data={"follower":follower_list})


@main.route("/followed/<username>")
@login_required
def followed_user(username):
    followed_list=[]
    followed = Follow.query.join(User, User.id==Follow.follower_id).filter(User.username==username).all()
    for f in followed:
        followed_list.append({"user":f.followed.username})
    return jsonify(errno=1,data={"followed":followed_list})

@main.route("/followers/list")
def followers_list():
    return render_template("list.html")
