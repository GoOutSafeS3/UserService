import connexion
import datetime
import logging
import configparser
import sys
import os
from users.database import db
from users.utils import add_user
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

    "SQLALCHEMY_DATABASE_URI": "users.db", # the database path/name
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    "USE_MOCKS": False, # use mocks for external calls
    "TIMEOUT": 2,  # timeout for external calls
    "REST_SERVICE_URL": "http://127.0.0.1:8079", # restaurant microservice url
    "BOOK_SERVICE_URL": "http://127.0.0.1:8080"
}


def fake_data():
    birth = datetime.datetime.today() - datetime.timedelta(weeks=1564)
    add_user("Admin", "Admin", "admin@example.com", "admin", "46966711", birth, is_admin=True)
    add_user("Operatore", "Verdi", "operator@example.com", "operator", "46338411", birth, is_operator=True)
    add_user("Anna", "Rossi", "anna@example.com", "anna", "46968411", birth, ssn="ANNASSN4791DFGYU")
    add_user("Giulia", "Nani", "nani@example.com", "nani", "3939675681", birth)


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
                configuration = parser["CONFIG"]["CONFIG"]

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
    except Exception as e:
        logging.info("- GoOutSafe: Users CONFIGURATION ERROR: %s", e)
        logging.info("- GoOutSafe: Users RUNNING: Default Configuration")
        return DEFAULT_CONFIGURATION


def setup(application, config):
    if config["REMOVE_DB"]:  # remove the db file
        try:
            os.remove("bookings/" + config["SQLALCHEMY_DATABASE_URI"])
            logging.info("- GoOutSafe: Users Database Removed")
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

    return app


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