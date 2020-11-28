from flask_login import login_required, current_user

from tripadvisor.models import User, TripAdvisor, Comment, Love, Comment_like,Follow
from tripadvisor import dao, tasks


def update_aboutMe(username, row):
    record = tasks.find_user(username)
    
    record.city = row.get('city', None)
    record.website  = row.get('website', None)
    record.about_me = row.get('about_me', None) 
    dao.save(record)


def submit_comments(id, user, row):
    tripadvisor = TripAdvisor()
    restaurant = tripadvisor.find_by_id(id)

    c = Comment()
    c.rating = row.get('rating', None)
    c.friend = row.get('friend', None)
    c.review_title = row.get('review_title', None)
    c.review_content = row.get('review_content', None)
    c.booking_date = row.get('booking_date', None)
    c.takeout = row.get('takeout', None)
    c.vegetable = row.get('vegetable', None)
    c.disabled = row.get('disabled', None)
    c.star1 = row.get('star1', None)
    c.star2 = row.get('star2', None)
    c.star3 = row.get('star3', None)
    c.recommend_dish = row.get('recommend_dish', None)
    c.author = user._get_current_object()
    c.restaurant = restaurant

    dao.save(c)


def get_followers(username):
    followers    = tasks.find_followers(username)
    my_followers = tasks.find_current_followers(current_user)

    followers_list = []
    for f in my_followers:
        followers_list.append(f.followed.id)

    result = []
    for f in followers:
        row = {}
        row['city'] = f.follower.city
        row['name'] = f.follower.username
        row['about_me'] = f.follower.about_me
        row['follower_count'] = f.follower.followers.count()

        if f.follower.id != current_user.id:
            if f.follower.id in followers_list:
                row['follow_status'] = '關注中'
            else:
                row['follow_status'] = '追蹤'
        else:
            row['follow_status'] = '自己'

        result.append(row)
    
    return result


def followed_user(username):
    followed = tasks.find_followed(username)
    my_followerd = tasks.find_current_followerd(current_user)
    
    followerd_list = []
    for f in my_followerd:
        followerd_list.append(f.followed.id)
    
    result = []
    for f in followed:
        row = {}
        row['city'] = f.followed.city
        row['name'] = f.followed.username
        row['about_me'] = f.followed.about_me
        row['follower_count'] = f.followed.followers.count()

        if f.followed.id != current_user.id:
            if f.followed.id in followerd_list:
                row['follow_status'] = '關注中'
            else:
                row['follow_status'] = '追蹤'
        else:
            row['follow_status'] = '自己'
        result.append(row)
    
    return result


def get_favorit_comments(username):
    comment = tasks.author_following_comments(username)
    my_following_comments = tasks.my_following_comments(current_user.id)
                            
    comment_like = [u.id for u in my_following_comments]

    followed_id = [ i.followed_id for i in current_user.followed.all()]

    comments = []
    for c in comment:
        row = {}
        row['follow_condition'] = '關注中' if c.author_id in followed_id else '追蹤' if c.author_id!=current_user.id else "自己"
        row['like_condition'] = '已讚' if c.id in comment_like else '讚'
        row['review_content'] = c.review_content
        row['rating'] = c.rating
        row['author'] = c.author.username
        row['title'] = c.restaurant.title

        comments.append(row)

    return comments


def visted_pages():
    records = tasks.get_recent_read(current_user.id)
    pages = []
    for record in records:
        row = {}
        row = record.to_dict()
        row['image'] = row['info_url'][3]
        pages.append(row)
    
    return pages


def query_restaurant(username):
    user = User()
    user = user.find_by_username(username)

    records, count = tasks.following_restaurant(user.id)
    
    restaurants = [ record.to_dict() for record in records ]

    return restaurants, count