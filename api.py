import datetime
from datetime import date
from flask import request, jsonify
from database import db, User
from errors import Error500, Error404, Error400
from utils import add_user, delete_user_


def get_users(ssn=None, phone=None, email=None, is_positive=None):
    users = db.session.query(User)
    if is_positive is not None:
        if is_positive == 'True':
            users = users.filter_by(is_positive=True).all()
            return jsonify([user.to_json() for user in users])
        else:
            users = users.filter_by(is_positive=False).all()
            return jsonify([user.to_json() for user in users])
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
    user_email = db.session.query(User).filter_by(email=req['email']).first()
    if user_email is not None:
        return Error400("The email already exist").get()
    user_phone = db.session.query(User).filter_by(phone=req['phone']).first()
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


def get_user_contacts(user_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    if user is None:
        return Error404("User not found").get()
    return {}
