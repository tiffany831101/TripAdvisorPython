from flask_login import login_required, current_user

from tripadvisor.models import User, TripAdvisor, Comment, Love, Comment_like,Follow


def submit_about_me(username, row):
    user = User.find_by_username(username)
    user.city = row.get("city", None)
    user.website = row.get("website", None)
    user.about_me = row.get("about_me", None) 
    return user


def submit_comments(user, row):
    restaurant =TripAdvisor.find_by_id(id)

    c = Comment()
    c.rating = row.get("rating",None)
    c.friend = row.get("friend",None)
    c.review_title = row.get("review_title",None)
    c.review_content = row.get("review_content", None)
    c.booking_date = row.get("booking_date", None)
    c.takeout = row.get("takeout",None)
    c.vegetable = row.get("vegetable",None)
    c.disabled = row.get("disabled", None)
    c.star1 = row.get("star1", None)
    c.star2 = row.get("star2", None)
    c.star3 = row.get("star3", None)
    c.recommend_dish = row.get("recommend_dish",None)
    c.author = user._get_current_object()
    c.restaurant = restaurant
    
    return c


def submit_comment_like(id, user):
    comment = Comment.find_by_id(id)

    c = Comment_like()
    c.user_id = user.id
    c.comment_id = comment.id
    return c


def submit_like(user, restaurant, row):
    focus = row.get("like", None)
    restaurant = TripAdvisor.find_by_name(restaurant)

    l = Love()
    l.focus = focus
    l.store = restaurant
    l.author = user._get_current_object()
    
    return l


def submit_unlike(current_user, restaurant):
    restaurant = TripAdvisor.find_by_name(restaurant)
    User.cancel_follow_restaurant(current_user.id, restaurant)
    return "OK"


def follow(username, current_user):
    user = User.find_by_username(username)
    if user is None:
        return {"status":"error","errmsg":"查無該用戶"}

    if current_user.is_following(user):
        return {"status":"error","errmsg":"已關注該用戶"}
    
    else:
        current_user.follow(user)
        return {"status":"success","msg":u"您已成功關注%s"%username}


def unfollow(username, current_user):
    user = User.find_by_username(username)
    if user is None:
        return {"status":"error","errmsg":"查無該用戶"}
    else:
        current_user.unfollow(user)
        return {"status":"success","msg":u"您已成功取消對%s的關注"%username}


def following_user(username):
    followers = Follow.find_followers(username)

    my_followers = Follow.find_current_followers(current_user)

    followers_list = []
    for f in my_followers:
        followers_list.append(f.followed.id)

    result = []
    for f in followers:
        row = {}
        row["city"] = f.follower.city
        row["user"] = f.follower.username
        row["about_me"] = f.follower.about_me
        row["follower_count"] = f.follower.followers.count()
        if f.follower.id != current_user.id:
            if f.follower.id in followers_list:
                row["follow_status"] = "關注中"
            else:
                row["follow_status"] = "追蹤"
        else:
            row["follow_status"] = "自己"

        result.append(row)
    
    return result


def followed_user(username):
    followed  = Follow.find_followed(username)

    my_followerd =  Follow.find_current_followerd(current_user)

    followerd_list=[]
    for f in my_followerd:
        followerd_list.append(f.followed.id)
    
    result = []
    for f in followed:
        row = {}
        row["city"] = f.followed.city
        row["about_me"] = f.followed.about_me
        row["follower_count"] = f.followed.followers.count()

        if f.followed.id != current_user.id:
            if f.followed.id in followerd_list:
                row["follow_status"] = "關注中"
            else:
                row["follow_status"] = "追蹤"
        else:
            row["follow_status"] = "自己"
        
        result.append(row)
    
    return result