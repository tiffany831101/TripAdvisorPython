from sqlalchemy import and_, func

from tripadvisor.models import User, TripAdvisor, Comment, Love,\
                                Comment_like, Follow, Reservation, Click
from tripadvisor import db


def get_user_id(user_id):
    if user_id != 1:
        variable = User.id
    else:
        user_id = 0
        variable = 0
    return user_id, variable

def cancel_follow_restaurant(id, restaurant):
    user = User()
    user = user.find_by_id(id=id).first()
    row  = user.restaurant_love.filter(TripAdvisor.id==restaurant.id).first()
    return db.session.delete(row)


def find_followed(username):
    return db.session.query(Follow).join(User, User.id==Follow.follower_id)\
                            .filter(User.username==username).all()


def find_current_followerd(current_user):        
    return db.session.query(Follow).join(User, User.id==Follow.follower_id)\
                            .filter(User.id==current_user.id).all()


def find_followers(username):
    return db.session.query(Follow).join(User, User.id==Follow.followed_id)\
                            .filter(User.username==username).all()


def find_current_followers(current_user):
    return db.session.query(Follow).join(User, User.id==Follow.followed_id)\
                    .filter(User.id==current_user.id)


def following_restaurant(user_id):
    restaurant =  db.session.query(TripAdvisor)\
                    .join(Love, Love.store_id == TripAdvisor.id)\
                    .filter(Love.user_id == user_id)

    count = restaurant.count()
    restaurants = restaurant.all()
    return restaurants, count


def cancel_follow_restaurant(id, restaurant):
    user = db.session.query(User).filter_by(id=id).first()
    row  = user.restaurant_love.filter(TripAdvisor.id==restaurant.id).first()
    return db.session.delete(row)


def cancel_follow_comments(user_id, comment):
        user = db.session.query(User).filter_by(id=user_id).first()
        row  = user.comment_like.filter(Comment.id==comment.id).first()
        return db.session.delete(row)


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


def comment_search(user_id, params):
        user_id, variable = get_user_id(user_id)

        return db.session.query(TripAdvisor, User.username)\
                        .outerjoin(Love,TripAdvisor.id==Love.store_id)\
                        .outerjoin(User, and_(Love.user_id==variable, User.id==user_id))\
                        .filter(*params)\
                        .order_by(TripAdvisor.rating_count.desc())


def rating_search(user_id, params):
    user_id, variable = get_user_id(user_id)
    
    return db.session.query(TripAdvisor, User.username)\
                    .outerjoin(Love,TripAdvisor.id==Love.store_id)\
                    .outerjoin(User, and_(Love.user_id==variable, User.id==user_id))\
                    .filter(*params)\
                    .order_by(TripAdvisor.rating.desc())


def page_filter(user_id, page):
    user_id, variable = get_user_id(user_id)
    return db.session.query(TripAdvisor, User.username)\
                    .outerjoin(Love,TripAdvisor.id==Love.store_id)\
                    .outerjoin(User, and_(Love.user_id==variable, User.id==user_id))\
                    .filter(TripAdvisor.rating_count>200)\
                    .paginate(page=page, per_page=30, error_out= False)


def author_following_comments(username):
    return  db.session.query(Comment).join(Comment_like, 
                                        Comment_like.comment_id == Comment.id)\
                            .join(User,and_(Comment_like.user_id == User.id, User.username==username))\
                            .all()


def my_following_comments(user_id):
    return db.session.query(Comment_like)\
            .filter(Comment_like.user_id==user_id).all()


def get_recent_read(user_id):
    return db.session.query(TripAdvisor).join(Click, Click.store_id == TripAdvisor.id)\
                                        .join(User, and_(User.id == Click.user_id,User.id==user_id))\
                                        .distinct()\
                                        .order_by(Click.create_time.desc())\
                                        .limit(5)                                 