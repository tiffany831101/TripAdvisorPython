from flask import render_template, request, jsonify
from flask_login import login_required

from tripadvisor.reservation import services, booking
from tripadvisor.models import TripAdvisor, Reservation


@booking.route('/result')
@login_required
def result():
    reservations, histories = services.get_reservation_status()
    return render_template("result.html", reservation=reservations, history=histories)


@booking.route('/<restaurant>',methods=["POST","GET"])
@login_required
def reservation(restaurant):
    tripAdvisor = TripAdvisor()
    data = tripAdvisor.find_by_name(restaurant)
    if not data:
        return render_template("booking.html")
    return render_template("booking.html", data=data)


@booking.route('/check',methods=["POST"])
def reservation_check():
    data = request.form
    
    if not all ([data["restaurant"], data["people"], data["booking_date"], data["booking_time"]]):
        return jsonify(status="error", errmsg="參數不完整")
    
    result = services.reserve(data)
    return jsonify(result)


@booking.route('/revise/<order_id>',methods=["POST","GET"])
def order_revise(order_id):
    reservation = Reservation()
    data = reservation.find_by_orderId(order_id)
    return render_template("revise.html", data=data)


@booking.route('/order/cancel/<order_id>',methods=["POST"])
def order_cancel(order_id):
    reservation = Reservation()
    result = reservation.cancel_order(order_id)
    return jsonify(result)


@booking.route('/update',methods=["POST"])
def order_update():
    data = request.form

    if not all ([data["restaurant"], data["people"], data["booking_date"], data["booking_time"]]):
        return jsonify(status="error", errmsg="參數不完整")
    
    result = services.update_order(data)
    
    return jsonify(result)