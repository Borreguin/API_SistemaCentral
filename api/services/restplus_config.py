"""
    This file defines all the API's configuration - API Home Page
    Archivo que define la configuración de la API en General - página inicial de la API
    Adds:
        Logger to save all the problems in the API
        Error handler in case is needed
"""
import datetime as dt
import traceback

from flask import request
from flask_restplus import Api
from sqlalchemy.orm.exc import NoResultFound

from settings.initial_settings import LogDefaultConfig

""" DB config"""
# dup_key_error = "duplicate key error"

api_log = LogDefaultConfig("api_services.log").logger

api = Api(version='0.1', title='API SISTEMA CENTRAL',
          contact="Roberto Sánchez A, David Panchi, José Enríquez",
          contact_email="rg.sanchez.a@gmail.com, dpanchi@cenace.org.ec, jenriquez@cenace.org.ec",
          contact_url="https://github.com/Borreguin",
          description='This API allows to model and to calculate components of central system of EMS',
          ordered=False)


# Special JSON encoder for special cases:
def custom_json_encoder(o):
    # this deals with Datetime types:
    if isinstance(o, dt.datetime):
        return o.isoformat()


@api.errorhandler(Exception)
def default_error_handler(e):
    global api_log
    ts = dt.datetime.now().strftime('[%Y-%b-%d %H:%M:%S.%f]')
    msg = f"{ts} {request.remote_addr} {request.method} {request.scheme}" \
          f"{request.full_path}"
    api_log.error(msg)
    api_log.error(traceback.format_exc())
    if hasattr(e, 'data'):
        return dict(success=False, msg=str(e.data["errors"])), 400

    return dict(success=False, msg=str(e)), 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    api_log.warning(traceback.format_exc())
    return {'message': 'No se obtuvo resultado'}, 404
