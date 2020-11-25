from users.background import init_celery
import connexion
import datetime
import logging
import configparser
import sys
import os
from users.database import db, User
from users.utils import add_user, mark_positive_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
sys.path.append("./users/")

DEFAULT_CONFIGURATION = {

    "FAKE_DATA": False, # insert some default data in the database (for tests)
    "REMOVE_DB": False, # remove database file when the app starts
    "DB_DROPALL": False,
    "INTEGRATION_FAKE_DATA": False, # fake data used in integration tests

    "IP": "0.0.0.0", # the app ip
    "PORT": 8081, # the app port
    "DEBUG":True, # set debug mode

    "SQLALCHEMY_DATABASE_URI": "db/users.db", # the database path/name
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    "TIMEOUT": 2,  # timeout for external calls
    "REST_SERVICE_URL": "http://restaurants:8080", # restaurant microservice url
    "BOOK_SERVICE_URL": "http://bookings:8080/",

    "UNMARK_AFTER": 600, # celery config for updating the ratings
    "result_backend" : os.getenv("BACKEND", "redis://localhost:6379"),
    "broker_url" : os.getenv("BROKER", "redis://localhost:6379"),
}


def fake_data():
    birth = datetime.datetime.today() - datetime.timedelta(weeks=1564)
    if db.session.query(User).filter_by(email = 'gianni@example.com').first() is None:
        add_user("Gianni", "Barbuti", "gianni@example.com", generate_password_hash("gianni"), "46966711", birth - datetime.timedelta(weeks=500,days=40))

    if db.session.query(User).filter_by(email='daniele@example.com').first() is None:
        add_user("Daniele", "Verdi", "daniele@example.com", generate_password_hash("daniele"), "46338411", birth - datetime.timedelta(weeks=100,days=4))

    if db.session.query(User).filter_by(email='anna@example.com').first() is None:
        add_user("Anna", "Rossi", "anna@example.com", generate_password_hash("anna"), "46968411", birth, ssn="ANNASSN4791DFGYU")

    if db.session.query(User).filter_by(email='giulia@example.com').first() is None:
        add_user("Giulia", "Nani", "giulia@example.com", generate_password_hash("giulia"), "3939675681", birth- datetime.timedelta(weeks=100,days=21))

    if db.session.query(User).filter_by(email='admin@example.com').first() is None:
        add_user("Admin","Admin","admin@example.com",generate_password_hash("admin"),"3665479701", (birth - datetime.timedelta(weeks=600,days=10)),is_admin=True)

    if db.session.query(User).filter_by(email='health@example.com').first() is None:
        add_user("Health","Authority","health@example.com",generate_password_hash("health"),"557692170",birth,is_health=True)

    if db.session.query(User).filter_by(email='operator@example.com').first() is None:
        add_user('Operator',"Trial",'operator@example.com',generate_password_hash('operator'),'3245678432', birth, rest_id=1, is_operator=True)

    if db.session.query(User).filter_by(email='operator2@example.com').first() is None:
        add_user('Operator', "Trial2", 'operator2@example.com', generate_password_hash('operator'), '3245674421', birth, rest_id=2, is_operator=True)

    if db.session.query(User).filter_by(email='operator3@example.com').first() is None:
        add_user('Operator', "Trial3", 'operator3@example.com', generate_password_hash('operator'), '3245421324', birth, rest_id=3, is_operator=True)

    if db.session.query(User).filter_by(email='operator4@example.com').first() is None:
        add_user('Operator', "Trial4", 'operator4@example.com', generate_password_hash('operator'), '4536721215', birth, rest_id=4, is_operator=True)

    if db.session.query(User).filter_by(email='operator5@example.com').first() is None:
        add_user('Operator', "Trial5", 'operator5@example.com', generate_password_hash('operator'), '4536741121', birth, rest_id=None, is_operator=True)

    if db.session.query(User).filter_by(email='operator6@example.com').first() is None:
        add_user('Operator', "Trial6", 'operator6@example.com', generate_password_hash('operator'), '6457812732', birth, rest_id=None, is_operator=True)

    if db.session.query(User).filter_by(email='alice@example.com').first() is None:
        add_user("Alice", "Vecchio", "alice@example.com", generate_password_hash("alice"), "463366711", birth + datetime.timedelta(weeks=23, days=40), ssn="TESTALICESSN1234")

    if mark_positive_user(13):
        print('Marked')


def get_config(configuration=None):
    """
    Returns a json file containing the configuration to use in the app
    The configuration to be used can be passed as a parameter,
    otherwise the one indicated by default in config.ini is chosen
    ------------------------------------
    [CONFIG]
    CONFIG = The_default_configuration
    ------------------------------------
    Params:
        - configuration: if it is a string it indicates the configuration to choose in config.ini
    """
    try:
        parser = configparser.ConfigParser()
        if parser.read('config.ini'):

            if type(configuration) != str:  # if it's not a string, take the default one
                configuration = parser["CONFIG"]["CONFIG"] # pragma: no cover

            logging.info("- GoOutSafe: Users CONFIGURATION: %s", configuration)
            configuration = parser._sections[configuration]  # get the configuration data

            parsed_configuration = {}
            for k, v in configuration.items():  # Capitalize keys and translate strings (when possible) to their relative number or boolean
                k = k.upper()
                parsed_configuration[k] = v
                try:
                    parsed_configuration[k] = int(v)
                except:
                    try:
                        parsed_configuration[k] = float(v)
                    except:
                        if v == "true":
                            parsed_configuration[k] = True
                        elif v == "false":
                            parsed_configuration[k] = False

            for k, v in DEFAULT_CONFIGURATION.items():
                if not k in parsed_configuration:  # if some data are missing enter the default ones
                    parsed_configuration[k] = v

            return parsed_configuration
        else:
            return DEFAULT_CONFIGURATION
    except Exception as e: # pragma: no cover
        logging.info("- GoOutSafe: Users CONFIGURATION ERROR: %s", e)
        logging.info("- GoOutSafe: Users RUNNING: Default Configuration")
        return DEFAULT_CONFIGURATION


def setup(application, config):
    if config["REMOVE_DB"]:  # remove the db file
        try:
            os.remove("users/" + config["SQLALCHEMY_DATABASE_URI"])
            logging.info("- GoOutSafe: Users Database Removed") # pragma: no cover
        except:
            pass

    config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + config["SQLALCHEMY_DATABASE_URI"]

    for k, v in config.items():
        application.config[k] = v  # insert the requested configuration in the app configuration

    db.init_app(application)

    if config["DB_DROPALL"]:  # remove the data in the db
        logging.info("- GoOutSafe: Users Dropping All from Database...")
        db.drop_all(app=application)

    db.create_all(app=application)

    if config["FAKE_DATA"]:  # add fake data (for testing)
        logging.info("- GoOutSafe: Users Adding Fake Data...")
        with application.app_context():
            fake_data()


def create_app(configuration=None):
    logging.basicConfig(level=logging.INFO)

    app = connexion.App(__name__)
    app.add_api('./api.yaml')
    application = app.app

    conf = get_config(configuration)
    logging.info(conf)
    logging.info("- GoOutSafe: Users ONLINE @ (" + conf["IP"] + ":" + str(conf["PORT"]) + ")")
    with app.app.app_context():
        setup(application, conf)

    init_celery(application)
    
    return app

def create_worker_app():
    configuration = os.getenv("CONFIG", "TEST")
    logging.basicConfig(level=logging.INFO)

    app = connexion.App(__name__)
    app.add_api('./api.yaml')
    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application = app.app

    conf = get_config(configuration)
    for k,v in conf.items():
        application.config[k] = v # insert the requested configuration in the app configuration

    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + application.config["SQLALCHEMY_DATABASE_URI"]
    db.init_app(application)
    init_celery(application)

    return application


if __name__ == '__main__':

    c = None
    if len(sys.argv) > 1:  # if it is inserted
        c = sys.argv[1]  # get the configuration name from the arguments

    app = create_app(c)

    with app.app.app_context():
        app.run(
            host=current_app.config["IP"],
            port=current_app.config["PORT"],
            debug=current_app.config["DEBUG"]
        )