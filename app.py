import connexion
import datetime
import logging
from database import db
from utils import add_user


def fake_data():
    birth = datetime.datetime.today() - datetime.timedelta(weeks=1564)
    add_user("Admin", "Admin", "admin@example.com", "admin", "46966711", birth, is_admin=True)
    add_user("Operatore", "Verdi", "operator@example.com", "operator", "46338411", birth, is_operator=True)
    add_user("Anna", "Rossi", "anna@example.com", "anna", "46968411", birth, ssn="ANNASSN4791DFGYU")


def create_app(conf=None):
    logging.basicConfig(level=logging.INFO)
    app = connexion.App(__name__)
    app.add_api('api.yaml')
    application = app.app
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    db.init_app(application)
    if conf is not None:
        db.drop_all(app=application)
        db.create_all(app=application)
        with app.app.app_context():
            fake_data()
    else:
        db.create_all(app=application)

    @application.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    return app


if __name__ == '__main__':
    app = create_app('TEST')
    app.run(port=8081)
