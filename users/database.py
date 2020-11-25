from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rest_id = db.Column(db.Integer)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    phone = db.Column(db.Unicode(128), unique=True)
    ssn = db.Column(db.Unicode(128), unique=True, default=None, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    is_operator = db.Column(db.Boolean, default=False)
    is_health_authority = db.Column(db.Boolean, default=False)
    is_positive = db.Column(db.Boolean, default=False)
    positive_datetime = db.Column(db.DateTime)

    def to_json(self):
        js = {}
        for attr in ('id', 'rest_id', 'firstname', 'lastname',
                     'email', 'phone', 'ssn',
                     'dateofbirth', 'is_active','is_anonymous',
                     'is_admin', 'is_health_authority','is_operator',
                     'password','is_positive',
                     'positive_datetime'):
            js[attr] = getattr(self, attr)
        return js