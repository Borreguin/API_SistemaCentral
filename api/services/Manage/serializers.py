from settings import initial_settings as init
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
        """ serializer for root component """
        self.rootcomponent = api.model("rootcomponent", {
            "block": fields.String(required=True,
                                   description="Nombre del bloque al que pertenece el componente"),
            "name": fields.String(required=True, description="nombre del componente")
        })

        """ serializer for root component """
        self.rootcomponentname = api.model("rootcomponentname", {
            "name": fields.String(required=True, description="Nombre del componente")
        })

        """ serializer for internal component """
        self.internalcomponent = api.model("internalcomponent", {
            "name": fields.String(required=True, description="Nombre del componente internal")
        })

        """ serializador para bloque root """
        self.blockroot = api.model("blockroot", {
            "name": fields.String(required=True, description="nombre del bloque root")
        })

        """ serializador para componente leaf """
        self.componentleaf = api.model("componentleaf", {
            "name": fields.String(required=True, description="nombre del componente leaf")
        })

        """ serializador para actualización de posición """
        self.position = api.model("position", {
            "pos_x": fields.Float(required=True, description="La posición x"),
            "pos_y": fields.Float(required=True, description="La posición y")
        })

        def recursive_operations(iteration_number=10):
            operation_fields = {
                "public_id": fields.String(required=True, description="Id público de la operación"),
                "name": fields.String(required=True, description="Nombre de la operación"),
                "type": fields.String(required=True, description=f"{init.AVAILABLE_OPERATIONS}"),
                "operator_ids": fields.List(fields.String, required=True),
                "position_x_y": fields.List(fields.Float, required=False, default=[0, 0])
            }
            """ serializador para añadir operación """
            if iteration_number:
                operation_fields["operations"] = fields.List(fields.Nested(recursive_operations(iteration_number-1),
                                                                           description="Operación interna"))
            return api.model(f'operation_{str(iteration_number)}', operation_fields)

        self.operations = recursive_operations()

        """ Ejemplo: 
        {"SERIE": ['id1', 'id2' ,
                    {"PARALELO": ['id3', 'id4']},
                    {"PARALELO": [{'SERIE': ['id5', 'id6']}, 'id7'}]
                    ]
        }       
        """
        """ serializador para operacion """
        self.operation = api.model("topología", {
        "topology": fields.Raw(required=True, description="La operación a realizar",
                               default=dict(SERIE=['id1','id2',dict(PARALELO=['id3','id4']),dict(PARALELO=[dict(SERIE=['id5','id6']),'id7'])]))
        })

        return api
