import datetime
from flask import request, jsonify
from werkzeug.security import check_password_hash
import requests
from database import db, User
from errors import Error500, Error404, Error400
from utils import add_user, delete_user_

URL_BOOKINGS = 'http://127.0.0.1:8080'
URL_RESTAURANTS = "http://127.0.0.1:8079"
TIMEOUT = 0.003  # timeout for external get


def get_users(ssn=None, phone=None, email=None, is_positive=None):
    users = db.session.query(User)
    if is_positive is not None:
        if is_positive == 'True':
            users = users.filter_by(is_positive=True).all()
    if ssn is not None:
        user = users.filter_by(ssn=ssn).first()
        if user is None:
            return Error404("User not found").get()
        return user.to_json(), 200
    if phone is not None:
        user = users.filter_by(phone=int(phone)).first()
        if user is None:
            return Error404("User not found").get()
        return user.to_json(), 200
    if email is not None:
        user = users.filter_by(email=email).first()
        if user is None:
            return Error404("User not found").get()
        return user.to_json(), 200
    return jsonify([user.to_json() for user in users]), 200


def create_user():
    req = request.json
    ssn = ''
    is_health = False
    is_operator = False
    is_admin = False
    exist_ssn = None
    firstname = req['firstname']
    lastname = req['lastname']
    email = req['email']
    password = req['password']
    password_repeat = req['password_repeat']
    phone = req['phone']
    dateofbirth = req['dateofbirth']
    try:
        ssn = req['ssn']
        is_health = req['is_health_authority']
        is_operator = req['is_operator']
        is_admin = req['is_admin']
    except:
        pass

    if password != password_repeat:
        return Error400("Passwords do not match").get()

    exist_email = db.session.query(User).filter_by(email=email).first()
    exist_phone = db.session.query(User).filter_by(phone=phone).first()

    if ssn != '':
        exist_ssn = db.session.query(User).filter_by(ssn=ssn).first()

    if exist_email is not None or exist_phone is not None or exist_ssn is not None:
        return Error400("The User already exist").get()

    today = datetime.datetime.today()
    if datetime.datetime.strptime(dateofbirth[:10], '%Y-%m-%d') > today:
        return Error400("Date Birth error").get()

    response = add_user(firstname,
                        lastname,
                        email,
                        password,
                        phone,
                        datetime.datetime.strptime(dateofbirth[:10], '%Y-%m-%d'),
                        is_health, is_operator, is_admin)
    return response


def get_id_user(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return Error404("User not found").get()
    return user.to_json()


def edit_user(user_id):
    req = request.json
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return Error404("User not found").get()

    checked = check_password_hash(user.password, req['old_password'])

    if checked:

        if req['password'] != req['password_repeat']:
            return Error400("Passwords do not match").get()

        user_email = db.session.query(User).filter_by(email=req['email']).first()
        if user_email is not None:
            if user_email.id != user_id:
                return Error400("The email already exist").get()
        user_phone = db.session.query(User).filter_by(phone=req['phone']).first()
        if user_phone is not None:
            if user_phone.id != user_id:
                return Error400("The phone already exist").get()
        try:
            user.firstname = req['firstname']
            user.lastname = req['lastname']
            user.email = req['email']
            dateofbirth = req['dateofbirth']
            user.dateofbirth = datetime.datetime.strptime(dateofbirth[:10], '%Y-%m-%d')
            user.set_password(req['password'])
            user.phone = req['phone']
            if req['is_positive'] == 'True':
                user.is_positive = True
                user.positive_datetime = datetime.datetime.today()
            if req['ssn'] == '':
                user.ssn = None
            else:
                user_ssn = db.session.query(User).filter_by(ssn=req['ssn']).first()
                if user_ssn is not None and user_ssn.id != user_id:
                    return Error400("The ssn already exist").get()
                user.ssn = req['ssn']
            db.session.commit()
        except:
            db.session.rollback()
            return Error500().get()
    else:
        return Error400("Old password error").get()
    return user.to_json()


def delete_user(user_id):
    """
    inserire controllo email e password
    e che non sia positivo

    controllare se e' operatore e ha ristorante con prenotazioni
    """
    return delete_user_(user_id)


def get_user_contacts(user_id, begin=None, end=None):
    if begin is None and end is None:
        end = datetime.datetime.today()
        begin = end - datetime.timedelta(weeks=2)
    else:
        return Error400("Specify both dates or none").get()
    user_contacts = []
    user = db.session.query(User).filter(User.id == user_id).first()
    if user is None:
        return Error404("User not found").get()
    try:  # get the user's bookings
        reply = requests.get(URL_BOOKINGS + '/bookings', timeout=TIMEOUT, params={'user_id': user_id,
                                                                                  'begin': begin,
                                                                                  'end': end})
    except:  # exception on getting the user's bookings
        return Error400("Error during user booking request, Try again").get()
    if reply.status_code == 200:
        bookings = reply.json()
    else:
        return Error400("Booking Service error, Try again").get()
    for booking in bookings:
        try:  # get the restaurant of the booking
            restaurant = requests.get(URL_RESTAURANTS + '/restaurants/' + booking['restaurant_id'], timeout=TIMEOUT)
            if restaurant.status_code == 200:
                restaurant = restaurant.json()
            else:
                return Error400("Restaurant Service error, Try again").get()
        except:  # exception on getting the restaurant of the booking
            return Error400("Error during restaurant request, Try again").get()

        # get the occupation time of the restaurant
        interval = datetime.timedelta(hours=restaurant['occupation_time'])
        end = booking['entrance_datetime'] + interval
        begin = booking['entrance_datetime'] - interval

        try:  # get the bookings (of the same restaurant) in the occupation time interval
            contact_bookings = requests.get(URL_BOOKINGS + '/bookings', timeout=TIMEOUT,
                                            params={'restaurant_id': booking['restaurant_id'],
                                                    'begin_entrance': begin,
                                                    'end_entrance': end})
        except:
            return Error400("Error during bookings (of the same restaurant) request, Try again").get()
        if contact_bookings.status_code == 200:
            contact_bookings = contact_bookings.json()
        else:
            return Error400("Booking Service error, Try again").get()
        for contact in contact_bookings:
            user_id_contact = contact['user_id']
            if user_id_contact != user_id:
                user_contact = db.session.query(User).filter_by(id=user_id_contact).first()
                if user_contact is not None:
                    user_contact = user_contact.to_json()
                    # insert the contact in the list
                    user_contacts.append(user_contact)

    return jsonify(user_contacts), 200
