from flask_login import current_user

import random
from datetime import datetime
import time

from tripadvisor.models import TripAdvisor, Reservation
from tripadvisor import tasks, dao


def reserve(data):
    order_id = "%s-%s" % (int(round(time.time() * 1000)),random.randint(0, 99999999))
    tripAdvisor = TripAdvisor()
    store = tripAdvisor.find_by_name(data['restaurant'])
    result = Reservation(
                        order_id = order_id,
                        title_name = data['restaurant'],
                        people = data['people'],
                        booking_date = data['booking_date'],
                        booking_time = data['booking_time'],
                        user = current_user._get_current_object(),
                        restaurant_id = store.id)
    result = dao.save(result)
    return order_id


def query_histories():
    now = datetime.now().strftime('%Y-%m-%d')
    records = tasks.get_history_result(now, current_user)
    histories = []
    for record in records:
        row = {}
        row['title'] = record[0].title_name
        row['date']  = record[0].booking_date.strftime('%Y-%m-%d')
        row['order_id'] = record[0].order_id
        row['image'] = record[1].info_url.split(',')[1]
        histories.append(row)
    return histories
    

def query_order():
    now = datetime.now().strftime('%Y-%m-%d')
    records = tasks.get_reservation_result(now, current_user)

    reservations = []
    for record in records:
        row = {}
        row['title']  = record[0].title_name
        row['people'] = record[0].people
        row['date'] = record[0].booking_date.strftime('%Y-%m-%d')
        row['order_id'] = record[0].order_id
        row['booking_time'] = record[0].booking_time
        row['image'] = record[1].info_url.split(',')[0]
        reservations.append(row)
    return reservations