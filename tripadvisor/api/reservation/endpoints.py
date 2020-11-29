from flask import render_template, request, jsonify
from flask_login import login_required

from tripadvisor.api.reservation import services, booking
from tripadvisor.models import TripAdvisor, Reservation

import logging

logger = logging.getLogger()


@booking.route('/result')
@login_required
def result():
    return render_template('result.html')


@booking.route('/revise/<order_id>', methods=['POST', 'GET'])
def order_revise(order_id):
    return render_template('revise.html')


@booking.route('/<restaurant>', methods=['POST', 'GET'])
@login_required
def reservation(restaurant):
    data = TripAdvisor().find_by_name(restaurant)
    return render_template('booking.html', data=data)


@booking.route('/check', methods=['POST'])
def reservation_check():
    """訂單添加功能"""
    res = {'status': False}
    try:
        data = request.form

        if not all ([data['restaurant'], data['people'], data['booking_date'], data['booking_time']]):
            res['msg'] = 'Lack of required parameters'
            return jsonify(res)
        
        order_id = services.reserve(data)
        res.update({'status': True, 'data': order_id})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@booking.route('/order/cancel', methods=['POST'])
def order_cancel():
    """訂單取消功能"""
    res = {'status': False}
    try:
        data = request.form
        if 'order_id' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res)

        Reservation().cancel_order(data['order_id'])
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@booking.route('/update', methods=['POST'])
def order_update():
    """訂單修改功能"""
    res = {'status': False}
    try:
        data = request.form

        if not all ([data['restaurant'], data['people'], data['booking_date'], data['booking_time']]):
            res['msg'] = 'Lack of required parameters'
            return jsonify(res)
        
        Reservation().update(data['order_id'], booking_date = data['booking_date'], \
                        people = data['people'], booking_time = data['booking_time']) 
                        
        res.update({'status': True})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@booking.route('/order/histories')
@login_required
def order_histories():
    """查詢歷史訂單"""
    res = {'status': False}
    try:
        histories = services.query_histories()
        res.update({'status': True, 'data':histories})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@booking.route('/orders')
@login_required
def order_result():
    """查詢未過期的訂單"""
    res = {'status': False}
    try:
        orders = services.query_order()
        res.update({'status': True, 'data': orders})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)


@booking.route('/order')
@login_required
def orders():
    """查詢當前訂單"""
    res = {'status': False}
    try:
        data = request.args.to_dict()
        if 'order_id' not in data:
            res['msg'] = 'Lack of required parameters'
            return jsonify(res)

        order = services.query_current_order(data['order_id'])
        res.update({'status': True, 'data': order})
        return jsonify(res)
    
    except Exception as e:
        logger.error(e)
        return jsonify(res)