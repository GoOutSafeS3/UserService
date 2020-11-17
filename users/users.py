import datetime
from flask import request, jsonify, abort
from database import db, User
from errors import Error500, Error404, Error400, Error
from utils import add_user, delete_user_


def get_users(ssn=None, phone=None, email=None, is_positive=None):
    getUsersPositive = False
    getUsersFilter = False
    users = db.session.query(User).all()
    return jsonify([user.to_json() for user in users])


def create_user():
    req = request.json
    firstname = req['firstname']
    lastname = req['lastname']
    email = req['email']
    ssn = req['ssn']
    password = req['password']
    password_repeat = req['password_repeat']
    phone = req['phone']
    dateofbirth = req['dateofbirth']
    is_health =  req['is_health_authority']
    is_operator = req['is_operator']
    is_admin = req['is_admin']

    if password != password_repeat:
        return Error400("Passwords do not match").get()

    exist_email = db.session.query(User).filter(User.email == email).first()
    exist_phone = db.session.query(User).filter(User.phone == phone).first()

    if ssn != '':
        exist_ssn = db.session.query(User).filter(User.ssn == ssn).first()

    if exist_email is not None or exist_phone is not None or exist_ssn is not None:
        return Error400("The User already exist").get()

    today = datetime.datetime.today()
    day, month, year = (int(x) for x in dateofbirth.split('/'))
    birth_date = today.replace(year=year, month=month, day=day)
    if birth_date > today:
        return Error400("Date Birth error").get()

    response = add_user(firstname,
                        lastname,
                        email,
                        password,
                        phone,
                        dateofbirth,
                        is_health, is_operator, is_admin)
    return response


def get_id_user(user_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return Error404("User not found").get()
    return user.to_json()


def edit_user(user_id):
    req = request.json
    user = db.session.query(User).filter(User.id == user_id).first()
    user_email = db.session.query(User).filter(User.email == req['email']).first()
    if user_email is not None:
        return Error400("The email already exist").get()
    user_phone = db.session.query(User).filter(User.phone == req['phone']).first()
    if user_phone is not None:
        return Error400("The phone already exist").get()
    if not user:
        return Error404("User not found").get()
    try:
        user.firstname = req['firstname']
        user.lastname = req['lastname']
        user.email = req['email']
        user.set_password(req['password'])
        user.phone = req['phone']
        if req['is_positive'] is True:
            user.is_positive = True
            user.positive_datetime = datetime.datetime.today()
        user.ssn = req['ssn']
        db.session.commit()
    except:
        db.session.rollback()
        return Error500("Server error, try again").get()
    return user.to_json()


def delete_user(user_id):
    return delete_user_(user_id)


def get_contacts(user_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    if user is None:
        return Error404("User not found").get()
