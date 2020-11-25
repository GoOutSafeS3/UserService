import datetime
from flask import current_app
import requests as req
from users.database import User, db
from users.errors import Error500, Error400
from werkzeug.security import generate_password_hash, check_password_hash


def get_from(url, params=None):
    try:
        if params is not None:
            r = req.get(url, timeout=2, params=params)
        else:
            r = req.get(url, timeout=2)
        try:
            return r.json(), r.status_code
        except:  # pragma: no cover
            return {
                       "type": "about:blank",
                       "title": "Unexpected Error",
                       "status": r.status_code,
                       "detail": "Unexpected error occurs",
                   }, r.status_code
    except Exception as e:
        print(e)
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
    except Exception as e:
        print(e)
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
        return new_user.to_json(),201
    except Exception as e:
        print(e)  # pragma: no cover
        db.session.rollback()
        return Error500().get()


def delete_user_(user):
    try:
        db.session.delete(user)
        db.session.commit()
        return {
                   "type": 'Success delete',
                   "title": 'user deleted successfully',
                   "status": 204,
                   "detail": '',
               }, 204
    except Exception as e: # pragma : no cover
        print(e)
        db.session.rollback()
        return Error500().get()


def unmark_positive_user(id_user): # pragma: no cover
    user = db.session.query(User).filter_by(id=id_user).first()
    if user is not None:
        try:
            user.is_positive = False
            user.positive_datetime = None
            db.session.commit()
            return True
        except:  # pragma: no cover
            db.session.rollback()
            return False


def mark_positive_user(id_user):
    user = db.session.query(User).filter_by(id=id_user).first()
    if user is not None:
        try:
            user.is_positive = True
            user.positive_datetime = datetime.datetime.today()
            db.session.commit()
            return True
        except:  # pragma: no cover
            db.session.rollback()
            return False
