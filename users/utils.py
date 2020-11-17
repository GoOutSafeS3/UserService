from flask import current_app
from database import User, db
from errors import Error500, Error404


def add_user(firstname, lastname, email, password, phone, dateofbirth, is_health=None, is_operator=None, is_admin=None):
    new_user = User()
    try:
        new_user.firstname = firstname
        new_user.lastname =lastname
        new_user.email = email
        new_user.set_password(password=password)
        new_user.phone = phone
        new_user.dateofbirth = dateofbirth
        if is_health is not None and is_operator is None and is_admin is None:
            new_user.is_health_authority = is_health
        if is_operator is not None and is_admin is None and is_health is None:
            new_user.is_operator = is_operator
        if is_admin is not None and is_health is None and is_operator is None:
            new_user.is_admin = is_admin
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_json()
    except:
        db.session.rollback()
        return Error500("Server error, try again").get()


def delete_user_(user_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    if user is None:
        return Error404("User not found").get()
    try:
        db.session.delete(user)
        db.session.commit()
        return {
            "type": 'success delete',
            "title": 'user deleted successfully',
            "status": 201,
            "detail": '',
        }
    except:
        db.session.rollback()
        return Error500("Server error, try again").get()