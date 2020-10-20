from settings.initial_settings import SUPPORTED_FORMAT_DATES as time_formats
from flask_restplus import fields, Model

import datetime as dt

"""
    Configure the API HTML to show for each services the schemas that are needed 
    for posting and putting
    (Explain the arguments for each service)
    Los serializadores explican los modelos (esquemas) esperados por cada servicio
"""


class Serializers:

    def __init__(self, app):
        self.api = app

    def add_serializers(self):
        api = self.api

        # añadir los serializadores
        """ serializer for user information """
        self.user = api.model("User", {
            "user_name": fields.String(required=True,
                                      description="Nombre del usuario"),
            "email": fields.String(required=True, description="Email del usuario"),
            "password": fields.String(required=True, description="Password del usuario"),
            "is_blocked": fields.Boolean(required=False, default=False, description="Usuario bloqueado, no se permite "
                                                                "eliminación/edición")
        })

        return api
