from database import User, db
from errors import Error500


def add_user(firstname, lastname, email, password, phone, dateofbirth,
             rest_id=None, ssn=None, is_health=None, is_operator=None, is_admin=None):
    new_user = User()
    try:
        new_user.firstname = firstname
        new_user.lastname = lastname
        new_user.email = email
        new_user.set_password(password=password)
        new_user.phone = phone
        new_user.dateofbirth = dateofbirth
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
    except: # pragma : no cover
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