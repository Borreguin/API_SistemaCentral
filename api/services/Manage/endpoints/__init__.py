# this script share common variables between all the scripts that are inside this folder

from api.services.restplus_config import api                        # Api Object with restplus settings
from settings import initial_settings as init                       # Initial settings
from api.services.restplus_config import default_error_handler      # default error handler
# Default error handler acts in case the error is not controlled in the lower level
# from api import db                                                  # Use of default DataBase
from api.services.Manage import serializers                         # Serializers used in this Endpoint
from api.services.Manage import parsers                             # Parsers used in this Endpoint


# Global variables to use inside the scripts in this package
log = init.LogDefaultConfig("ws_sRemoto.log").logger
ns = api.namespace('management', description='Relativas a la administración de usuarios, grupos y recursos')

