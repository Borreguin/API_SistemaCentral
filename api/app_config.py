# This script allows the flask configuration
# Created by Roberto Sánchez A.
# Gerencia de Desarrollo Técnico - CENACE
# Septiembre 2020

# General imports:
from api import *

# import custom configuration:
from flask_mongoengine import MongoEngine

from settings import initial_settings as init


# DataBase SQLite Configuration
def create_app():
    app = Flask(__name__)                   # Flask application
    app = configure_app(app)                # general swagger configuration
    db_configurations(app)                  # database configurations
    log_after_request(app)                  # configurations for log after request
    return app


def configure_app(app):
    """
    Configuración general de la aplicación API - SWAGGER
    :return:
    """
    app.config['SWAGGER_UI_DOC_EXPANSION'] = init.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    app.config['RESTPLUS_VALIDATE'] = init.RESTPLUS_VALIDATE
    app.config['RESTPLUS_MASK_SWAGGER'] = init.RESTPLUS_MASK_SWAGGER
    app.config['ERROR_404_HELP'] = init.RESTPLUS_ERROR_404_HELP
    app.config['SECRET_KEY'] = init.SECRET_KEY
    return app


def db_configurations(app):
    app.config['MONGODB_SETTINGS'] = init.MONGOCLIENT_SETTINGS
    db = MongoEngine(app)
    if init.MONGO_LOG_LEVEL == "ON":
        print("WARNING!! El log de la base de datos MongoDB está activado. "
              "Esto puede llenar de manera rápida el espacio en disco")


def log_after_request(app):

    @app.after_request
    def after_request(response):
        """ Logging after every request. """
        # This avoids the duplication of registry in the log,
        # since that 500 is already logged via @logger_api
        ts = dt.datetime.now().strftime('[%Y-%b-%d %H:%M:%S.%f]')
        msg = f"{ts} {request.remote_addr} {request.method} {request.scheme}" \
              f"{request.full_path} {response.status}"
        if 200 >= response.status_code < 400:
            log.info(msg)
        elif 400 >= response.status_code < 500:
            log.warning(msg)
        elif response.status_code >= 500:
            log.error(msg)
        return response