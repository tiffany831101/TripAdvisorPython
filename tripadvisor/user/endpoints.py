from flask import request, jsonify
from flask_login import login_required, current_user

from tripadvisor import dao
from tripadvisor.models import Comment 
from tripadvisor.user import user, services


@user.route('/restaurant/like/<restaurant>')
def like(restaurant):
    submit = services.submit_like(current_user, restaurant, request.args)
    result = dao.save(submit)
    return jsonify(result)


@user.route('/restaurant/unlike/<restaurant>')
def unlike(restaurant):
    submit = services.submit_unlike(current_user, restaurant)
    result = dao.delete()
    return jsonify(result)


@user.route("/about_me/<username>",methods=["POST"])
@login_required
def about_me(username):
    submit = services.submit_about_me(username, request.form)
    result = dao.save(submit)
    return jsonify(result)


@user.route("/comment/like/<id>")
def comment_like(id):
    submit = services.submit_comment_like(id, current_user)
    result = dao.save(submit)
    return result


@user.route("/comment/unlike/<int:id>")
def comment_unlike(id):
    comment = Comment.find_by_id(id)
    User.cancel_follow_comments(current_user.id, comment)
    result = dao.delete()
    return jsonify(result)


@user.route('/comment/edit/<int:id>',methods=["POST"])
def review_edit(id):
    submit = services.submit_comments(id, current_user, request.form)
    result = dao.save(submit)
    return jsonify(result)


@user.route('/follow/<username>')
@login_required
def follow(username):
    result = services.follow(username, current_user)
    return jsonify(result)
    

@user.route('/unfollow/<username>')
@login_required
def unfollow(username):
    result = services.unfollow(username, current_user)
    return jsonify(result)


@user.route("/followers/<username>")
@login_required
def follow_user(username):
    followers = services.following_user(username)
    return jsonify(status = "success", followers=followers)


@user.route("/followed/<username>")
@login_required
def followed_user(username):
    followed = services.followed_user(username)
    return jsonify(status = "success", followed=followed)
