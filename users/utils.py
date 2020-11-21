import datetime
from flask import current_app
import requests as req
from users.database import User, db
from users.errors import Error500, Error400

#
# ----------------------------------MOCK DATA--------------------------------
#

""" 
Restaurants and Bookings mock
They are identified starting from 1.
"""

bookings_mock = [

]

restaurants_mock = [
    {
        "url": "/restaurants/1",  # NO OPENING TIMES
        "id": 1,
        "name": "Rest 1",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": None,
        "first_closing_hour": None,
        "second_opening_hour": None,
        "second_closing_hour": None,
        "occupation_time": 0,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": [1, 2, 3, 4, 5, 6, 7]
    },
    {
        "url": "/restaurants/2",  # ONLY AT LUNCH (CLOSED ON MONDAYS)
        "id": 2,
        "name": "Rest 2",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": 10,
        "first_closing_hour": 14,
        "second_opening_hour": None,
        "second_closing_hour": None,
        "occupation_time": 1,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": [1]
    },
    {
        "url": "/restaurants/3",  # ALWAYS OPEN (NEVER CLOSED)
        "id": 3,
        "name": "Rest 3",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": 0,
        "first_closing_hour": 23,
        "second_opening_hour": 0,
        "second_closing_hour": 0,
        "occupation_time": 2,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": []
    },
    {
        "url": "/restaurants/4",  # TWO OPENINGS (CLOSED ON SUNDAY AND MONDAYS)
        "id": 4,
        "name": "Rest 4",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": 10,
        "first_closing_hour": 12,
        "second_opening_hour": 20,
        "second_closing_hour": 23,
        "occupation_time": 2,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": [1, 7]
    }
]

""" 
The list of tables (for restaurant mock)
They are identified starting from 1.
"""

tables = [
    [{"id": 1, "capacity": 4}],
    [{"id": 2, "capacity": 3}],
    [{"id": 4, "capacity": 5}, {"id": 5, "capacity": 4}, {"id": 6, "capacity": 2}],
    [{"id": 3, "capacity": 2}]
]


#
# --------------------------SERVICES UTILITY FUNCTIONS----------------------------
#

def get_from(url, params=None):
    try:
        if params is not None:
            r = req.get(url, timeout=2, params=params)
        else:
            r = req.get(url, timeout=2)
        try:
            return r.json(), r.status_code
        except:
            return {
                       "type": "about:blank",
                       "title": "Unexpected Error",
                       "status": r.status_code,
                       "detail": "Unexpected error occurs",
                   }, r.status_code
    except:
        return {
                   "type": "about:blank",
                   "title": "Internal Server Error",
                   "status": 500,
                   "detail": "Error during communication with other services",
               }, 500


def delete_from(url):
    try:
        r = req.delete(url, timeout=current_app.config["TIMEOUT"])
        try:
            return r.json(), r.status_code
        except:
            return {
                       "type": "about:blank",
                       "title": "Unexpected Error",
                       "status": r.status_code,
                       "detail": "Unexpected error occurs",
                   }, r.status_code
    except:
        return {
                   "type": "about:blank",
                   "title": "Internal Server Error",
                   "status": 500,
                   "detail": "Error during communication with other services",
               }, 500

#
# -----------------------------------------------------------------------------------
#


def add_user(firstname, lastname, email, password, phone, dateofbirth,
             rest_id=None, ssn=None, is_health=None, is_operator=None, is_admin=None):
    new_user = User()
    try:
        new_user.firstname = firstname
        new_user.lastname = lastname
        new_user.email = email
        new_user.password = password
        new_user.phone = phone
        new_user.dateofbirth = dateofbirth
        new_user.is_positive = False
        if ssn is not None:
            new_user.ssn = ssn
        if is_health is not None and is_operator is None and is_admin is None:
            new_user.is_health_authority = is_health
        if is_operator is not None and is_admin is None and is_health is None:
            new_user.is_operator = is_operator
        if is_admin is not None and is_health is None and is_operator is None:
            new_user.is_admin = is_admin
        if rest_id is not None:
            new_user.rest_id = rest_id
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_json()
    except:  # pragma : no cover
        db.session.rollback()
        return Error500().get()


def delete_user_(user):
    try:
        db.session.delete(user)
        db.session.commit()
        return {
                   "type": 'Success delete',
                   "title": 'user deleted successfully',
                   "status": 201,
                   "detail": '',
               }, 201
    except:  # pragma : no cover
        db.session.rollback()
        return Error500().get()


def mark_positive_user(id_user):
    user = db.session.query(User).filter_by(id=id_user).first()
    if user is not None:
        try:
            user.is_positive = True
            user.positive_datetime = datetime.datetime.today()
            db.session.commit()
            return True
        except:  # pragma : no cover
            db.session.rollback()
            return False
