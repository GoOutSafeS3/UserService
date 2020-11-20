import datetime
from flask import request, jsonify, current_app
import requests
from users.database import db, User
from users.errors import Error500, Error404, Error400
from users.utils import add_user, delete_user_, get_from, delete_from, bookings_mock
from users.utils import restaurants_mock

URL_BOOKINGS = 'http://127.0.0.1:8080'
URL_RESTAURANTS = "http://127.0.0.1:8079"
TIMEOUT = 2  # timeout for external get


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
        if req['is_positive']:
            user.is_positive = True
            user.positive_datetime = datetime.datetime.today()
        if req['ssn'] == '':
            user.ssn = None
        else:
            user_ssn = db.session.query(User).filter_by(ssn=req['ssn']).first()
            if user_ssn is not None and user_ssn.id != user_id:
                return Error400("The ssn already exist").get()
            user.ssn = req['ssn']
        if user.is_operator and req['rest_id'] != 'None':
            user.rest_id = int(req['rest_id'])
        db.session.commit()
    except:
        db.session.rollback()
        return Error500().get()

    return user.to_json()


def delete_user(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return Error404('User not found').get()

    if user.is_positive is True:  # if the user is Covid-19 positive he can not delete his data
        return Error400("You cannot delete your data as long as you are positive").get()

    with current_app.app_context():
        if current_app.config["USE_MOCKS"]:
            return { }
        else:
            if user.is_operator and user.rest_id is not None:  # the user is operator with restaurant

                url = URL_BOOKINGS + '/bookings'
                params = {'rest_id': user.rest_id,
                          'begin': datetime.datetime.today()}
                bookings = get_from(url, params)
                if bookings.status_code == 200:
                    bookings = bookings.json()
                else:
                    return Error400('BookingService error').get()
                if bookings:
                    return Error400(
                        "you cannot delete the account if you have active reservations in your restaurant").get()
                else:
                    url = URL_RESTAURANTS + '/restaurants/' + user.rest_id
                    resp = delete_from(url)  # return a response
                    if resp.status_code == 200 or resp.status_code == 201:
                        return delete_user_(user)
                    else:
                        return Error400('Error on try to delete the restaurant').get()

            else:  # the user is not operator

                params = {'user_id': user_id, 'begin': datetime.datetime.today()}
                url = URL_BOOKINGS + '/bookings'
                bookings = get_from(url=url, params=params)
                if bookings.status_code == 200:
                    bookings = bookings.json()
                else:
                    return Error400('BookingService error').get()
                if bookings:
                    return Error400("you cannot delete the account if you have active reservations").get()

    return delete_user_(user)


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
    with current_app.app_context():
        if current_app.config["USE_MOCKS"]:
            pass
        else:
            params = {'user_id': user_id,
                      'begin': begin,
                      'end': end}
            resp = get_from(URL_BOOKINGS + '/bookings', params=params)
            if resp.status_code == 200:
                bookings = resp.json()
            else:
                return Error400('BookingService error').get()
            for booking in bookings:
                restaurant = get_from(URL_RESTAURANTS + '/restaurants/' + booking['restaurant_id'])
                if restaurant.status_code == 200:
                    restaurant = restaurant.json()
                else:
                    return Error400("Restaurant Service error, Try again").get()

                # get the occupation time of the restaurant
                interval = datetime.timedelta(hours=restaurant['occupation_time'])
                end = booking['entrance_datetime'] + interval
                begin = booking['entrance_datetime'] - interval

                # get the bookings (of the same restaurant) in the occupation time interval
                contact_bookings = get_from(URL_BOOKINGS + '/bookings',
                                            params={'restaurant_id': booking['restaurant_id'],
                                                    'begin_entrance': begin,
                                                    'end_entrance': end})

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
