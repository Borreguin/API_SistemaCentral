"""
COMPONENT ROOT- BASE DE DATOS PARA SISTEMA CENTRAL
START DATE: 10/11/2020
DP V.2
"""

from dto.mongo_engine_handler.Components.Comp_Leaf import *
from temp import utils as u
from mongoengine import *
import datetime as dt
from settings import initial_settings as init
from dto.mongo_engine_handler.Info.Consignment import *


class ReportSource(Document):
    report_id = StringField(required=True, default=None)
    root_id = StringField(required=True, default=None)
    leaf_id = StringField(required=True, default=None)
    tipo = StringField(required=True, default="Reporte Fuentes")
    fuente = StringField(choices=tuple(init.AVAILABLE_SOURCES))
    fecha_inicio = DateTimeField(required=True)
    fecha_final = DateTimeField(required=True)
    updated = DateTimeField(default=dt.datetime.now())
    responsable=StringField(required=True, default=None)
    consignaciones_detalle = ListField(EmbeddedDocumentField(Consignment), required=False)
    periodo_indisponibilidad=ListField(required=False)
    disponibilidad_porcentage = FloatField(required=False, min_value=-1, max_value=100)
    tiempo_calculo_minutos = FloatField(default=0)
    observaciones = DictField(required=False, default=dict())
    disponibilidad_minutos = FloatField(default=0)
    indisponibilidad_minutos = FloatField(default=0)
    meta = {"collection": "REPORT|Fuentes"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.report_id is None:
            # id = str(uuid.uuid4())
            self.report_id = str(uuid.uuid4())
        if self.updated is None:
            self.updated= dt.datetime.now()
        if self.responsable is None:
            self.responsable='Usuario Generico'

    #TODO: AÑADIR FUNCIONES NECESARIAS

    def __repr__(self):
        return f"<Root {self.updated},{self.report_id},{self.root_id},{len(self.leaf_id)}>"

    def __str__(self):
        return f"<Root {self.updated},{self.report_id},{self.root_id},{len(self.leaf_id)}>"

