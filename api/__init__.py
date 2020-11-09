from api.app_config import create_app
#from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = create_app()
#db = SQLAlchemy(app)
#migrate = Migrate(app, db)

""" Note: import the models that migrate will track changes therefore don´t delete the next line """
# from dto.sqlite_engine_handler import Users, Groups, Roles, Resources