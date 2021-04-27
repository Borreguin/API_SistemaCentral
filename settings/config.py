# API de Authentfication usando JWT
# Configuraciones iniciales de la API
import os
config = dict()
config["name"] = "API Sistema Central "
config["API_URL_PREFIX"] = "api-sct"
config["version"] = "0.4"
config["PORT"] = 7821
config["DEBUG_PORT"] = 5000
config["FLASK_DEBUG"] = True

config["RESTPLUS_SWAGGER_UI_DOC_EXPANSION"] = "list"
config["RESTPLUS_VALIDATE"] = True
config["RESTPLUS_MASK_SWAGGER"] = False
config["RESTPLUS_ERROR_404_HELP"] = False

# MONGODB CONFIGURATION
config["MONGOCLIENT_SETTINGS"] = {"host": "localhost", "port": 2717, "db": "DB_DISP_EMS"}
config["MONGO_LOG_LEVEL"] = {"value": "OFF", "options": ["ON", "OFF"]}

# User configurations
config["ADMIN_NAME"] = "admin"
config["INITIAL_ADMIN_EMAIL"] = "admin@local.com"
config["INITIAL_ADMIN_PASSWORD"] = "123456"

# Log configurations
config["ROTATING_FILE_HANDLER_HELP"] = "https://docs.python.org/3.6/library/logging.handlers.html#logging.handlers.RotatingFileHandler.__init__",
config["ROTATING_FILE_HANDLER"] = {"filename": "auth_app.log", "maxBytes": 5000000, "backupCount": 5, "mode": "a"}
config["ROTATING_FILE_HANDLER_LOG_LEVEL"] = {"value": "info", "options": ["error", "warning", "info", "debug", "off"]}

# Repositories:
# if there are need for nested repositories, they should be write as: path\\of\\this\\repository
config["TEMP_REPO"] = "temp"
config["LOG_REPO"]="logs"
# TODO: Redireccionar a una carpeta única
config["DB_REPO"] = "_db"
# REPOSITORIO CONSIGNACIONES
config["CONSIGNACIONES"] = os.path.join(config["DB_REPO"], "consignaciones")

config["SUPPORTED_FORMAT_DATES"] = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f"]
config["DEFAULT_DATE_FORMAT"] = "%Y-%m-%d %H:%M:%S"

#CALCULOS DISPONIBLES
config["AVAILABLE_OPERATIONS"] = ["LEAF", "ROOT", "PARALELO", "SERIE", "PONDERADO", "PROMEDIO", "INTERMEDIO"]
config["AVAILABLE_SOURCES"] = [None, "MANUAL", "BD SIST.REMOTO", "HISTORICO"]

