from flask_sqlalchemy import SQLAlchemy
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import datetime
import hashlib
import random
from app.utlis.captcha.captcha import captcha

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column (db.String(10),unique=True)

    def __repr__(self):
        return '<Role %r>' %self.name


class Follow(db.Model):
    __tablename__='follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin,db.Model):
    __tablename__='user'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column (db.String(20),unique=True,index=True,nullable=False)
    email = db.Column(db.String(40),unique=True,nullable=False)
    cellphone = db.Column(db.Integer,nullable=False)
    password_hash = db.Column(db.String(128))
    gender =db.Column(db.String(5))
    image_url = db.Column(db.String(32))
    birthday = db.Column(db.String(10))
    id_number = db.Column(db.String(10),unique=True)
    country = db.Column(db.String(3))
    address = db.Column(db.Text())
    LINE  = db.Column(db.String(20))
    
    survey =db.relationship('Survey',backref='survey')
    reservation = db.relationship('Reservation',backref='user',lazy='dynamic')
    restaurant_comment = db.relationship('Comment',backref='author',lazy='dynamic')
    restaurant_love = db.relationship('Love',backref='author',lazy="dynamic")
    
    confirmed = db.Column(db.Boolean,default=False)
    


    name = db.Column(db.String(20))
    location = db.Column(db.String(30))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    
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
    
    @property
    def password(self):
        raise AttributeError ('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash =generate_password_hash(password)
    
    def verify_password(self, password):
        """
        檢驗密碼的正確性
        :params passwd: 用戶登入時填寫的原始密碼
        : return : 如果正確返回True，否則返回False
        """
        return check_password_hash(self.password_hash, password)
    
    
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"],expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed =True
        db.session.add(self)
        return True
    def ping(self):
        self.last_seen=datetime.utcnow()
        db.session.add(self)
    


    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
            
    def is_followed_by(self,user):
        return self.followers.filter_by(followed_id=user.id).first() is not None


    def __repr__(self):
        return '<User %r>' %self.name

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

class BaseModel(object):
    """"模型基類，為每個模型補充創建時間與更新時間"""
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime,default=datetime.now, onupdate=datetime.now)

class Food(BaseModel, db.Model):
    """食物"""
    __tablename__="food"
    id = db.Column(db.Integer,primary_key=True)
    foodname = db.Column(db.String(12))

class Survey(BaseModel, db.Model):
    """顧客滿意度調查"""
    __tablename__="survey"
    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.Date)
    price = db.Column(db.Integer)
    satisfication= db.Column(db.String(1))
    opinion =db.Column(db.Text())
    intention = db.Column(db.String(1))
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    foods = db.relationship("Food",secondary="popular_food")


favorite_food=db.Table(
    "popular_food",
    db.Column("survey_id",db.Integer, db.ForeignKey('survey.id'),primary_key=True),
    db.Column("food_id",db.Integer, db.ForeignKey('food.id'),primary_key=True)
)


class Reservation(BaseModel,db.Model):
    __tablename__="reservation"
    id = db.Column(db.Integer,primary_key=True)
    title_name = db.Column(db.String(20))
    people = db.Column(db.Integer())
    booking_date = db.Column(db.Date)
    booking_time = db.Column(db.String(10))
    order_id1 = db.Column(db.String(40))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    restaurant = db.relationship('TripAdvisor',backref='reservation',lazy='dynamic')

class TripAdvisor(db.Model):
    __tablename__ = "ta"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(50))
    res_type = db.Column(db.String(20))
    rating_count = db.Column(db.Integer())
    info_url = db.Column(db.String(512))
    cellphone = db.Column(db.String(20))
    address = db.Column(db.String(128))
    street =db.Column(db.String(20))
    rating = db.Column(db.Float())
    comment = db.Column(db.String(1024))
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'))
    user_comment = db.relationship("Comment",backref="restaurant",lazy="dynamic")
    following = db.relationship("Love",backref="store",lazy="dynamic")
    def to_basic_dict(self):
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

class Love(BaseModel,db.Model):
    _tablename__="love"
    id = db.Column(db.Integer, primary_key=True)
    focus = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    storeid = db.Column(db.Integer,db.ForeignKey('ta.id'))