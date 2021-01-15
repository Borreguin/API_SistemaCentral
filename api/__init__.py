""" General imports """
import os
import json
import sys
import copy
from flask import Blueprint
from flask import send_from_directory
import datetime as dt
from flask import Flask
from flask import request

# añadiendo a sys el path del proyecto:
# permitiendo el uso de librerías propias:
api_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(api_path)
sys.path.append(api_path)
sys.path.append(project_path)

from api.app_config import create_app
from settings import initial_settings as init

app = create_app()

""" global variables """
log = init.LogDefaultConfig("app_flask.log").logger

""" Note: import the models that migrate will track changes therefore don´t delete the next line """
# from dto.sqlite_engine_handler import Users, Groups, Roles, Resources
