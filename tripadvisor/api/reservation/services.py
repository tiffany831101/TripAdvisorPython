from flask_login import current_user

import random
from datetime import datetime
import time

from tripadvisor.models import TripAdvisor, Reservation
from tripadvisor import tasks, dao


def reserve(data):
    order_id = "%s-%s" % (int(round(time.time()*1000)),random.randint(0,99999999))
    tripAdvisor = TripAdvisor()
    store = tripAdvisor.find_by_name(data["restaurant"])
    result = Reservation(
                        order_id1 = order_id,
                        title_name = data["restaurant"],
                        people = data["people"],
                        booking_date = data["booking_date"],
                        booking_time = data["booking_time"],
                        user = current_user._get_current_object(),
                        restaurant_id = store.id)
    result = dao.save(result)
    return result


def get_reservation_status():
    now = datetime.now().strftime("%Y-%m-%d")
    result = tasks.get_reservation_result(now, current_user)

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
    
    history = tasks.get_history_result(now, current_user)
    histories = []
    for h in history:
        row = {}
        row["title"] = h[0].title_name
        row["date"] = h[0].booking_date
        row["order_id"] = h[0].order_id1
        row["image"] = h[1].info_url.split(",")[0]
        histories.append(row)
    
    return reservations, histories


def update_order(data):
    reservation = Reservation()
    result = reservation.update(data["order_id"], \
                    **{"people":data["people"], "booking_date":data["booking_date"], \
                        "booking_time":data["booking_time"]})
    return result