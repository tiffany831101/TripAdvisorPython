from flask_login import current_user

import random
from datetime import datetime
import time

from tripadvisor.models import TripAdvisor, Reservation


def reserve(restaurant, people, booking_date, booking_time):
    order_id = "%s-%s" % (int(round(time.time()*1000)),random.randint(0,99999999))
        
    store = TripAdvisor.find_by_name(restaurant)
    result = Reservation(title_name = restaurant,
                        people = people,
                        booking_date = booking_date,
                        booking_time = booking_time,
                        order_id1 = order_id,
                        user = current_user._get_current_object(),
                        restaurant_id=store.id)
    return result


def get_reservation_status():
    now = datetime.now().strftime("%Y-%m-%d")
    result = Reservation.get_reservation_result(now, current_user)

    reservations = []
    for r in result:
        row = {}
        row["title"] = r[0].title_name
        row["people"] = r[0].people
        row["date"] = r[0].booking_date
        row["booking_time"] = r[0].booking_time
        row["order_id"] = r[0].order_id1
        row["image"] = r[1].info_url.split(",")[0]
        reservations.append(row)
    
    history = Reservation.get_history_result(now, current_user)
    histories = []
    for h in history:
        row = {}
        row["title"] = h[0].title_name
        row["date"] = h[0].booking_date
        row["order_id"] = h[0].order_id1
        row["image"] = h[1].info_url.split(",")[0]
        histories.append(row)
    
    return reservations, histories

