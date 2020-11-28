from sqlalchemy import and_, func, distinct

from tripadvisor.models import User, TripAdvisor, Comment, Love,\
                                Comment_like, Follow, Reservation, Click
from tripadvisor import db, dao


def get_user_id(user_id):
    if user_id != 0:
        variable = User.id
    else:
        user_id = 0
        variable = 0
    return user_id, variable


def cancel_follow_restaurant(id, restaurant):
    user = User()
    user = user.find_by_id(id=id).first()
    row  = user.restaurant_love.filter(TripAdvisor.id==restaurant.id).first()
    return dao.delete(row)


def find_followed(username):
    return db.session.query(Follow)\
                    .join(User, User.id == Follow.follower_id)\
                    .filter(User.username == username)\
                    .all()


def find_current_followerd(current_user):        
    return db.session.query(Follow)\
                    .join(User, User.id == Follow.follower_id)\
                    .filter(User.id == current_user.id)\
                    .all()


def find_followers(username):
    return db.session.query(Follow)\
                        .join(User, User.id == Follow.followed_id)\
                        .filter(User.username == username)\
                        .all()


def find_current_followers(current_user):
    return db.session.query(Follow)\
                    .join(User, User.id == Follow.follower_id)\
                    .filter(User.id == current_user.id)


def following_restaurant(user_id):
    restaurant =  db.session.query(TripAdvisor)\
                        .join(Love, Love.store_id == TripAdvisor.id)\
                        .filter(Love.user_id == user_id)

    counts = restaurant.count()
    restaurants = restaurant.all()
    return restaurants, counts


def unfollow_restaurant(id, restaurant):
    restaurant = db.session.query(TripAdvisor).filter(TripAdvisor.title == restaurant).first()
    user = db.session.query(User).filter_by(id = id).first()
    row  = user.restaurant_love.filter(TripAdvisor.id == restaurant.id).first()
    dao.delete(row)


def follow_restaurant(user, restaurant):
    restaurant = db.session.query(TripAdvisor).filter(TripAdvisor.title == restaurant).first()
    row = Love(store=restaurant, author=user._get_current_object())
    dao.save(row)


def unlike_comment(user_id, comment):
    user = db.session.query(User).filter_by(id=user_id).first()
    row  = user.comment_like.filter(Comment.id==comment.id).first()
    return dao.delete(row)


def like_comment(id, current_user):
    comment = db.session.query(Comment).filter_by(id=id).first()
    comment = Comment_like(user_id = current_user.id, comment_id = comment.id)
    return dao.save(comment)


def get_reservation_result(now, current_user):
    return db.session.query(Reservation, TripAdvisor)\
                    .select_from(TripAdvisor)\
                    .outerjoin(Reservation, 
                                and_(Reservation.restaurant_id == TripAdvisor.id, 
                                    Reservation.booking_date > now))\
                    .join(User, and_(Reservation.user_id == User.id, User.id == current_user.id))\
                    .all()


def get_history_result(now, current_user):
    return db.session.query(Reservation, TripAdvisor)\
                .select_from(TripAdvisor)\
                .outerjoin(Reservation, 
                            and_(Reservation.restaurant_id == TripAdvisor.id,
                                Reservation.booking_date < now))\
                .join(User, and_(Reservation.user_id == User.id, User.id==current_user.id))\
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
                    .outerjoin(Love, TripAdvisor.id == Love.store_id)\
                    .outerjoin(User, and_(Love.user_id == variable, User.id == user_id))\
                    .filter(TripAdvisor.rating_count > 200)\
                    .paginate(page = page, per_page = 30, error_out = False)


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


def get_city():
    return db.session.query(TripAdvisor.city)\
                     .filter(TripAdvisor.city.isnot(None))\
                     .distinct()\
                     .all()


def get_area(city):
    return db.session.query(TripAdvisor.area)\
                     .filter(TripAdvisor.city == city)\
                     .distinct()\
                     .all()


def get_top10_restaurant():
    return db.session.query(TripAdvisor.title)\
                     .order_by(TripAdvisor.rating_count.desc())\
                     .limit(10)


def like_restaurant(id, user_id):
    return db.session.query(Love)\
                     .filter(and_(Love.user_id == user_id, Love.store_id == id))\
                     .first()


def get_comments(restaurant):
    restaurant = db.session.query(TripAdvisor.comment)\
                        .filter(TripAdvisor.title == restaurant)\
                        .first()
    return restaurant.comment.split(',')


def find_user(username):
    return db.session.query(User)\
                    .filter(User.username == username)\
                    .first()