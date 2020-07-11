from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import and_, func
from sqlalchemy.ext.declarative import declarative_base

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime

from tripadvisor import db, login_manager, dao

Base = declarative_base()


class BaseModel(object):
    """"模型基類，為每個模型補充創建時間與更新時間"""
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, \
                                        onupdate=datetime.now)


class Role(BaseModel, db.Model):
    __tablename__ = 'role'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column (db.String(10), unique=True)

    def __repr__(self):
        return '<Role %r>' %self.name


class Follow(BaseModel, db.Model):
    __tablename__='follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def find_followers(username):
        return db.session.query(Follow).join(User, User.id==Follow.followed_id)\
                            .filter(User.username==username).all()
    
    def find_current_followers(current_user):
        return db.session.query(Follow).join(User, User.id==Follow.followed_id)\
                            .filter(User.id==current_user.id).all()

    def find_followed(username):
        return db.session.query(Follow).join(User, User.id==Follow.follower_id)\
                            .filter(User.username==username).all()

    def find_current_followerd(current_user):        
        return db.session.query(Follow).join(User, User.id==Follow.follower_id)\
                            .filter(User.id==current_user.id).all()


class User(UserMixin, db.Model):
    __tablename__='user'
    __table_args__ = {"useexisting": True}

    id = db.Column(db.Integer,primary_key = True)
    username = db.Column (db.String(20),unique=True,index=True,nullable=False)
    email = db.Column(db.String(40),unique=True,nullable=False)
    cellphone = db.Column(db.String(10),nullable=False)
    password_hash = db.Column(db.String(128))
    gender =db.Column(db.String(5))
    image_url = db.Column(db.String(32))
    birthday = db.Column(db.String(10))
    id_number = db.Column(db.String(10),unique=True)
    country = db.Column(db.String(3))
    address = db.Column(db.Text())
    LINE  = db.Column(db.String(20))
    
    survey = db.relationship('Survey',backref='survey')
    reservation = db.relationship('Reservation',backref='user',lazy='dynamic')
    restaurant_comment = db.relationship('Comment',backref='author',lazy='dynamic')
    comment_son = db.relationship("Child_cmt",backref="author",lazy="dynamic")
    restaurant_love = db.relationship('Love',backref='author',lazy="dynamic")
    comment_like = db.relationship('Comment_like',backref='user',lazy="dynamic")
    click_store = db.relationship('Click',backref='user',lazy="dynamic")

    confirmed = db.Column(db.Boolean,default=False)
    
    city = db.Column(db.String(10))
    website = db.Column(db.String(128))
    about_me = db.Column(db.String(100))
    
    
    posts = db.relationship('Post', backref='author', lazy='dynamic')
   
    followed = db.relationship('Follow',
                                foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower',lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed',lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    
    def find_by_id(id):
        return db.session.query(User).filter_by(id=id).first()

    def find_by_email(email):
        return db.session.query(User).filter_by(email=email).first()

    def find_by_username(username):
        return db.session.query(User).filter_by(username=username).first()

    def find_by_cellphone(cellphone):
        return db.session.query(User).filter_by(cellphone=cellphone).first()

    def find_by_cellphone_and_email(cellphone, email):
        return db.session.query(User).filter(and_(User.cellphone==cellphone, User.email==email)).first()

    def update(id, **kwargs):
        db.session.query(User).filter_by(id=id).update(kwargs)
        return dao.update()

    def cancel_follow_restaurant(id, restaurant):
        user = db.session.query(User).filter_by(id=id).first()
        row  = user.restaurant_love.filter(TripAdvisor.id==restaurant.id).first()
        return db.session.delete(row)

    def cancel_follow_comments(user_id, comment):
        user = db.session.query(User).filter_by(id=user_id).first()
        row  = user.comment_like.filter(Comment.id==comment.id).first()
        return db.session.delete(row)


        

    @property
    def password(self):
        raise AttributeError ('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash =generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"],expiration)
        return s.dumps({'confirm':self.id})

 
    def ping(self):
        self.last_seen=datetime.utcnow()
        db.session.add(self)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            dao.save(f)
            
            
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            dao.delete()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
            
    def is_followed_by(self, user):
        return self.followers.filter_by(followed_id=user.id).first() is not None
    

    def page_load(val, page):
        if not val == 0:
            return db.session.query(TripAdvisor, User.username).outerjoin(Love,TripAdvisor.id==Love.store_id)\
                    .outerjoin(User, and_(Love.user_id==User.id, User.id==val)).filter(TripAdvisor.rating_count>200)\
                    .paginate(page=int(page),per_page=30,error_out= False)
                     
        else:
            return db.session.query(TripAdvisor, User.username).outerjoin(Love,TripAdvisor.id==Love.store_id)\
                    .outerjoin(User, and_(Love.user_id==0, User.id==0)).filter(TripAdvisor.rating_count>200)\
                    .paginate(page=int(page),per_page=30,error_out= False)

    def comment_search(val, params):
        if not val == 1:
            return db.session.query(TripAdvisor, User.username).outerjoin(Love,TripAdvisor.id==Love.store_id)\
                        .outerjoin(User, and_(Love.user_id==User.id, User.id==val)).filter(*params)\
                            .order_by(TripAdvisor.rating_count.desc())
        else:
            return db.session.query(TripAdvisor, User.username).outerjoin(Love,TripAdvisor.id==Love.store_id)\
                        .outerjoin(User, and_(Love.user_id==0, User.id==0)).filter(*params)\
                            .order_by(TripAdvisor.rating_count.desc())


    def rating_search(val, params):
        if not val == 1:
            return db.session.query(TripAdvisor, User.username).outerjoin(Love,TripAdvisor.id==Love.store_id)\
                        .outerjoin(User, and_(Love.user_id==User.id, User.id==val)).filter(*params)\
                        .order_by(TripAdvisor.rating.desc())
        else:
            return db.session.query(TripAdvisor, User.username).outerjoin(Love,TripAdvisor.id==Love.store_id)\
                        .outerjoin(User, and_(Love.user_id==0, User.id==0)).filter(*params)\
                        .order_by(TripAdvisor.rating.desc())

    def __repr__(self):
        return '<User %r>' %self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return '<User %r>' %self.author_id


class Survey(BaseModel, db.Model):
    __tablename__="survey"

    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.Date)
    price = db.Column(db.Integer)
    satisfication= db.Column(db.String(1))
    opinion =db.Column(db.Text())
    intention = db.Column(db.String(1))
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))


class Reservation(BaseModel,db.Model):
    __tablename__="reservation"

    id = db.Column(db.Integer,primary_key=True)
    title_name = db.Column(db.String(32))
    people = db.Column(db.Integer())
    booking_date = db.Column(db.Date)
    booking_time = db.Column(db.String(10))
    order_id1 = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey("ta.id"))

    def cancel_order(id):
        return db.session.query(Reservation).filter_by(order_id1=id).delete()

    def find_by_orderId(id):
        return db.session.query(Reservation).filter_by(order_id1=id).first()

    def get_reservation_result(now, current_user):
        return db.session.query(Reservation, TripAdvisor).select_from(TripAdvisor)\
                     .outerjoin(Reservation, and_(Reservation.restaurant_id == TripAdvisor.id, 
                                             Reservation.booking_date > now))\
                     .join(User, and_(Reservation.user_id == User.id, User.id == current_user.id))\
                     .all()


    def get_history_result(now, current_user):
        return db.session.query(Reservation, TripAdvisor).select_from(TripAdvisor)\
                    .outerjoin(Reservation, and_(Reservation.restaurant_id==TripAdvisor.id,
                                            Reservation.booking_date < now))\
                    .join(User, and_(Reservation.user_id==User.id, User.id==current_user.id))\
                    .order_by(Reservation.booking_date.desc())\
                    .all()

    def update(id, **kwargs):
        db.session.query(Reservation).filter_by(order_id1=id).update(kwargs)
        return dao.update()

class TripAdvisor(db.Model):
    __tablename__ = "ta"

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))
    res_type = db.Column(db.String(32))
    rating_count = db.Column(db.Integer())
    info_url = db.Column(db.Text())
    cellphone = db.Column(db.String(20))
    address = db.Column(db.String(128))
    street =db.Column(db.String(64))
    rating = db.Column(db.Float())
    comment = db.Column(db.Text())
    read_count = db.Column(db.Integer, server_default='0')
    open_time = db.Column(db.String(64))                  
    reservation = db.relationship('Reservation',backref='store',lazy='dynamic')
    user_comment = db.relationship("Comment",backref="restaurant",lazy="dynamic")
    following = db.relationship("Love",backref="store",lazy="dynamic")
    clicked_user = db.relationship("Click",backref="store",lazy="dynamic")

    def find_by_id(id):
        return db.session.query(TripAdvisor).get_or_404(id)

    def find_by_name(title):
        return db.session.query(TripAdvisor).filter_by(title=title).first()

    def to_dict(self):
        return {
            "id":self.id,
            "title":self.title,
            "res_type":self.res_type,
            "rating_count":self.rating_count,
            "info_url":self.info_url.split(","),
            "cellphone":self.cellphone,
            "address":self.address,
            "street":self.street,
            "rating":self.rating,
            "comment":self.comment.split(",")
        }


class Hotel(db.Model):
    __tablename__ = "hotel"

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(50))
    comment_count = db.Column(db.Integer())
    city = db.Column(db.String(12))
    address =db.Column(db.String(20))
    cellphone = db.Column(db.String(20))
    intro = db.Column(db.String(512))
    tourist = db.Column(db.String(128))
    star = db.Column(db.Float())
    comment = db.Column(db.Text())

class Comment(BaseModel,db.Model):
    __tablename__="comment"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    review_title = db.Column(db.String(50))
    review_content = db.Column(db.Text())
    friend = db.Column(db.Integer)
    booking_date = db.Column(db.Date)
    takeout = db.Column(db.Integer)
    vegetable = db.Column(db.Integer)
    service = db.Column(db.Integer)
    disabled = db.Column(db.Integer)
    star1 = db.Column(db.Integer)
    star2 = db.Column(db.Integer)
    star3 = db.Column(db.Integer)
    recommend_dish = db.Column(db.String(50))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    store_id = db.Column(db.Integer,db.ForeignKey('ta.id'))
    child_cmt = db.relationship("Child_cmt",backref="fcmt",lazy="dynamic")
    user_like = db.relationship("Comment_like",backref="comment",lazy="dynamic")


    def find_by_id(id):
        return db.session.query(Comment).get_or_404(id)
        

class Love(BaseModel,db.Model):
    _tablename__="love"

    id = db.Column(db.Integer, primary_key=True)
    focus = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    store_id = db.Column(db.Integer,db.ForeignKey('ta.id'))


class Child_cmt(BaseModel,db.Model):
    __tablename__="ccmt"

    id = db.Column(db.Integer, primary_key=True)
    review_title = db.Column(db.String(50))
    review_content = db.Column(db.Text())
    fcmt_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

class Comment_like(BaseModel,db.Model):
    __tablename__="comment_like"

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Click(BaseModel,db.Model):
    __tablename__="click"

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer,db.ForeignKey('ta.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
