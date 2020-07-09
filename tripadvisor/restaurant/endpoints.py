from flask import render_template, session, redirect, url_for, \
                  abort, flash, current_app, request, jsonify
from flask_login import login_required, current_user

from sqlalchemy import and_, func
from datetime import datetime
import time
import logging
import random
import json

from tripadvisor.restaurant import services, main
from tripadvisor.restaurant.forms import QueryForm, EditionProfileForm, PostForm, BookingForm
from tripadvisor import db, redis_store
import tripadvisor.settings.defaults
from tripadvisor.models import User, Role, Post, Survey, TripAdvisor, Reservation,\
                               Comment, Love, Comment_like,Follow, Click



logger = logging.getLogger()

@main.route('/restaurant')
def index():
    logger.error("error msg")
    logger.warn("warn msg")
    logger.info("info msg")
    logger.debug("debug msg")
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
            survey = current_user._get_current_object()
        )
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
    #收藏餐廳列表
    user, restaurants, count = services.favorit_restaurant_count(username)

    #收藏評論
    comments = services.favorit_comments(username)
    
    #最近瀏覽概況
    read = services.recent_read_page(username)

    return render_template('user.html',store_list=restaurants, count=count, comment_list=comments, user=user, read_list=read)


@main.route('/forum',methods=['GET','POST'])
def forum():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.forum'))
    
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc())\
                           .paginate(page,per_page=5,error_out=False)

    posts = pagination.items
    return render_template('forum.html', form=form, posts=posts, pagination=pagination)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',post=[post])


@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
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

    result = services.comment_result(survey)
    
    return jsonify(errno=0,data={"list":result})


@main.route('/reservation/<restaurant>',methods=["POST","GET"])
@login_required
def reservation(restaurant):
    data = TripAdvisor.query.filter_by(title=restaurant).first()
    if not data:
        return render_template("booking.html")
    return render_template("booking.html", data=data)


@main.route('/reservation/check',methods=["POST"])
def reservation_check():
    row = {}
    row["restaurant"] = request.form.get("restaurant")
    row["people"] = request.form.get("people")
    row["booking_date"] = request.form.get("booking_date")
    row["booking_time"] = request.form.get("booking_time")
    row["current_user"] = current_user
    result = save_reservation_check(row)

    return jsonify(result)


@main.route('/reservation/result')
@login_required
def result():
    reservations, histories = services.reservation_condition
    return render_template("result.html", reservation=reservations, history=histories)


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
    row = {}
    row["order_id"] = request.form.get("order_id")
    row["restaurant"] = request.form.get("restaurant")
    row["people"] = request.form.get("people")
    row["booking_date"] = request.form.get("booking_date")
    row["booking_time"] = request.form.get("booking_time")
    if len(list(row.keys())) != 4:
        return jsonify(errno=0,errmsg="參數不完整")
    r = Reservation.query.filter_by(order_id1=order_id).update(row)
    
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


@main.route("/restaurant/filter")
def restaurant_filter():
    page = request.args.get("page")
    if not page:
        page=int(1)
    user = current_user.get_id()
    redis_key = "restaurant_%s"  % (page)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type":"application/json"}

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
    resp_dict=dict(errno=1, data=data_list,total_page=total_page)
    resp_json = json.dumps(resp_dict)

    redis_key = "restaurant_%s" % (page)

    try:
        redis_store.hset(redis_key,page,resp_json)
        redis_store.expire(redis_key, RESTAURANT_LIST_PAGE)
    except Exception as e:
        current_app.logger.error(e)
    return resp_json, 200, {"Content-Type":"application/json"}
    

@main.route('/restaurant/search')
def restaurant_search():
    """獲取餐廳的列表信息(搜索頁面)"""
    address = request.args.get("area") #區域
    res_type = request.args.get("food") #餐廳類型
    sort_key = request.args.get("filter") #過濾類型
    page = request.args.get("page")
    keyword = request.args.get("keyword")
    params = {"area":address, "food":res_type, "filter":sort_key,"keyword":keyword}
    try:
        page = int(page)
    except Exception as e:
        logger.error(e)
        page = int(1)
    
    user = current_user.get_id()
    result = services.get_restaurant_info_from_redis(address, res_type, sort_key, page, keyword, user)
    if result:
        return result, 200, {"Content-Type":"application/json"}
    
    restaurant = services.get_restaurant_info_from_mysql(address, res_type, sort_key, page, keyword, user)

    restaurant_obj = restaurant.paginate(page=page,per_page=30,error_out= False)
    restaurant_li = restaurant_obj.items

    if not restaurant_li:
        return jsonify(errno="3",errmsg="參數錯誤")

    total_page = restaurant_obj.pages
    data_list=[]
    for d in restaurant_li:
        row = {}
        row["title"] = d[0].title
        row["rating_count"] = d[0].rating_count
        row["info_url"] = (d[0].info_url).split(",")[0]
        row["cellphone"] = d[0].cellphone
        row["street"] = d[0].street
        row["rating"] = d[0].rating
        row["count"] = d[0].read_count
        row["comment"] = (d[0].comment).split(",")[0]
        row["love"] = "已收藏" if current_user.get_id() is not None and d[1]==current_user.username else "收藏"
        data_list.append(row)
          
    resp_dict = dict(errno=1,data=data_list,total_page = total_page, params = params)
    resp_json = json.dumps(resp_dict)
    redis_key = "restaurant_%s_%s_%s_%s_%s_%s" % (address, res_type, sort_key, page, keyword, user)

    try:
        pipeline = redis_store.pipeline()
        pipeline.multi()
        pipeline.hset(redis_key, page, resp_json)
        pipeline.expire(redis_key, RESTAURANT_LIST_PAGE)
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)
    return resp_json, 200, {"Content-Type":"application/json"}


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
    restaurant={"title":data.title,"address":data.street,"image":data.info_url.split(",")[2] if data.info_url else None,"id":data.id}
    comment = Comment.query.filter(Comment.store_id==data.id).order_by(Comment.create_time.desc()).limit(3)
    comment_list=[]
    for c in comment:
        author = c.author.username
        title = c.review_title
        content = c.review_content
        rating = c.rating
        comment_list.append({"author":author,"title":title,"content":content,"rating":rating})
    return render_template("review.html",restaurant=restaurant,comment = comment_list)


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
    followers = services.follow_user(username)
    return jsonify(errno=1,data={"follower":followers})


@main.route("/followed/<username>")
@login_required
def followed_user(username):
    followeds = services.followed_user(username)
    return jsonify(errno=1,data={"followed":followeds})


@main.route("/about_me/<username>",methods=["POST"])
@login_required
def about_me(username):
    city = request.form.get("city")
    about_me = request.form.get("about_me")
    website = request.form.get("website")

    result = services.save_member_info(username, city, about_me, website)
    return jsonify(result)