"""
COMPONENTES EN BASE DE DATOS PARA SISTEMA CENTRAL
START DATE: 21/10/2020
DP V.1
"""
import hashlib
import traceback
from dto.mongo_engine_handler import log
from mongoengine import *
import datetime as dt
import uuid
from settings import initial_settings as init
from dto.mongo_engine_handler.Comp_Leaf import *


class Operations(EmbeddedDocument):
    calculation_type = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    updated = DateTimeField(default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.calculation_type is None:
            self.calculation_type = init.AVAILABLE_OPERATIONS[0]

    def parallel(self,inputs:list):
        check=[float(i) for i in inputs]
        if check:
            aux=1
            result=0
            for r in inputs:
                q=1-r
                result=result+(aux*q)
                aux=q
            return result



    def edit_leaf_component(self, new_internal: dict):
        try:

            to_update = ["nombre", "calculation_type"]
            for key, value in new_internal.items():
                if key in to_update:
                    setattr(self, key, value)
            self.updated = dt.datetime.now()

            return True, f"Componente interno editado"

        except Exception as e:

            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc()  # Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def update_position_x_y(self, pos_x: float, pos_y: float):
        self.position_x_y = [pos_x, pos_y]

    def __repr__(self):
        return f"<Leaf {self.name}>"

    def __str__(self):
        return f"<Leaf {self.name}>"

    def validate_leaf(self):
        return self.source is not None

    def to_dict(self):
        return dict(public_id=self.public_id, name=self.name, source=self.source, position_x_y=self.position_x_y)
