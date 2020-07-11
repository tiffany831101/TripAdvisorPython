from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from tripadvisor.reservation import services, booking
from tripadvisor import dao
from tripadvisor.models import User, TripAdvisor, Reservation


@booking.route('/<restaurant>',methods=["POST","GET"])
@login_required
def reservation(restaurant):
    data = TripAdvisor.query.filter_by(title=restaurant).first()
    if not data:
        return render_template("booking.html")
    return render_template("booking.html", data=data)


@booking.route('/check',methods=["POST"])
def reservation_check():
    restaurant = request.form.get("restaurant")
    people = request.form.get("people")
    booking_date = request.form.get("booking_date")
    booking_time = request.form.get("booking_time")

    if not all ([restaurant, people, booking_date, booking_time]):
        return jsonify(status="error", errmsg="參數不完整")

    result = services.reserve(restaurant, people, booking_date, booking_time)
    result = dao.save(result)

    return jsonify(result)


@booking.route('/result')
@login_required
def result():
    reservations, histories = services.get_reservation_status()
    return render_template("result.html", reservation=reservations, history=histories)


@booking.route('/revise/<order_id>',methods=["POST","GET"])
def order_revise(order_id):
    data = Reservation.find_by_orderId(order_id)
    return render_template("revise.html", data=data)


@booking.route('/order/cancel/<order_id>',methods=["POST"])
def order_cancel(order_id):
    data = Reservation.cancel_order(order_id)
    result = dao.delete()
    return jsonify(result)


@booking.route('/update',methods=["POST"])
def order_update():
    people = request.form.get("people")
    order_id = request.form.get("order_id")
    booking_date = request.form.get("booking_date")
    booking_time = request.form.get("booking_time")

    if not all([people, order_id, booking_date, booking_time]):
        return jsonify(status="error", errmsg="參數不完整")
    
    result = Reservation.update(order_id, **{"people":people, "booking_date":booking_date, "booking_time":booking_time})

    return jsonify(result)