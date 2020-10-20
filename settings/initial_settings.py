# Created by Roberto Sanchez at 3/29/2019
# -*- coding: utf-8 -*-
""" Set the initial settings of this application"""
import sys, datetime as dt
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import logging
import os
from .config import config as raw_config

""""
    Created by Roberto Sánchez A, rg.sanchez.a@gmail.com; you can redistribute it
    and/or modify it under the terms of the MIT License.
    If you need more information. Please contact the email: rg.sanchez.a@gmail.com
    "My work is well done to honor God at any time" R Sanchez A.
    Mateo 6:33
"""

""" script path"""
script_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(script_path)
api_path = os.path.join(project_path, "api")

print("Loading configurations from: " + script_path)
""" initial configuration coming from config.py"""
config = raw_config

"""" FLASK CONFIGURATION """
production_path = os.path.join(project_path, "Production_server.txt")
print(production_path, os.path.exists(production_path))
if os.path.exists(production_path):
    FLASK_DEBUG = False
    SECRET_KEY = "Change_me"
else:
    FLASK_DEBUG = config["FLASK_DEBUG"]
    SECRET_KEY = "Th1$1$a$6creTK6y"

""" JWT CONFIGURATION """
TOKEN_VALID_TIME = dt.timedelta(**config["TOKEN_VALID_TIME"])

""" API CONFIGURATION """
if config["API_URL_PREFIX"] != "/":
    API_URL_PREFIX = "/" + config["API_URL_PREFIX"]
PORT = config["PORT"]

""" Log file settings: """
log_file = config["ROTATING_FILE_HANDLER"]["filename"]
log_path = os.path.join(project_path, "logs")
log_file_name = os.path.join(log_path, log_file)
config["ROTATING_FILE_HANDLER"]["filename"] = log_file_name
ROTATING_FILE_HANDLER = config["ROTATING_FILE_HANDLER"]
ROTATING_FILE_HANDLER_LOG_LEVEL = config["ROTATING_FILE_HANDLER_LOG_LEVEL"]

""" Settings for Mongo Client"""
MONGOCLIENT_SETTINGS = config["MONGOCLIENT_SETTINGS"]
MONGO_LOG_LEVEL = config["MONGO_LOG_LEVEL"]["value"]
MONGO_LOG_LEVEL_OPTIONS = config["MONGO_LOG_LEVEL"]["options"]

""" SUPPORTED DATES """
SUPPORTED_FORMAT_DATES = config["SUPPORTED_FORMAT_DATES"]
DEFAULT_DATE_FORMAT = config["DEFAULT_DATE_FORMAT"]

""" SWAGGER CONFIGURATION """
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = config["RESTPLUS_SWAGGER_UI_DOC_EXPANSION"]
RESTPLUS_VALIDATE = config["RESTPLUS_VALIDATE"]
RESTPLUS_MASK_SWAGGER = config["RESTPLUS_MASK_SWAGGER"]
RESTPLUS_ERROR_404_HELP = config["RESTPLUS_ERROR_404_HELP"]

""" REPOSITORIES """
TEMP_PATH = config["TEMP_REPO"]
TEMP_PATH = os.path.join(project_path, TEMP_PATH)
if not os.path.exists(TEMP_PATH):
    os.makedirs(TEMP_PATH)

"""" REPOSITORIES CONFIGURATION """
TEMP_REPO = config["TEMP_REPO"]
DB_REPO = config["DB_REPO"]

""" LISTA DE REPOSITORIOS """
REPOS = [TEMP_REPO, DB_REPO]
FINAL_REPO = list()
for repo in REPOS:
    this_repo = os.path.join(project_path, repo)
    if not os.path.exists(this_repo):
        os.makedirs(this_repo)
    FINAL_REPO.append(this_repo)

# getting the definitive path for each one in same order:
TEMP_REPO, DB_REPO = FINAL_REPO


# Default Class for Logging messages about this API
class LogDefaultConfig():
    """
    Default configuration for the logger file:
    """
    rotating_file_handler = None

    def __init__(self, log_name: str = None):
        if log_name is None:
            log_name = "Default.log"

        self.log_file_name = os.path.join(log_path, log_name)
        self.rotating_file_handler = ROTATING_FILE_HANDLER
        self.rotating_file_handler["filename"] = self.log_file_name
        logger = logging.getLogger(log_name)
        formatter = logging.Formatter('%(levelname)s [%(asctime)s] - %(message)s')
        # creating rotating and stream Handler
        R_handler = RotatingFileHandler(**self.rotating_file_handler)
        R_handler.setFormatter(formatter)
        S_handler = StreamHandler(sys.stdout)
        # adding handlers:
        logger.addHandler(R_handler)
        logger.addHandler(S_handler)

        # setting logger in class
        self.logger = logger

        self.level = ROTATING_FILE_HANDLER_LOG_LEVEL["value"]
        options = ROTATING_FILE_HANDLER_LOG_LEVEL["options"]
        if self.level in options:
            if self.level == "error":
                self.logger.setLevel(logging.ERROR)
            if self.level == "warning":
                self.logger.setLevel(logging.WARNING)
            if self.level == "debug":
                self.logger.setLevel(logging.DEBUG)
            if self.level == "info":
                self.logger.setLevel(logging.INFO)
            if self.level == "off":
                self.logger.setLevel(logging.NOTSET)
        else:
            self.logger.setLevel(logging.ERROR)
