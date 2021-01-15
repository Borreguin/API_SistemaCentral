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

from dto.mongo_engine_handler.Consignment import *
from settings import initial_settings as init


class ComponenteLeaf(EmbeddedDocument):
    public_id = StringField(required=True, default=None)
    name = StringField(required=True)
    source = StringField(choices=tuple(init.AVAILABLE_SOURCES))
    updated = DateTimeField(default=dt.datetime.now())
    position_x_y = ListField(FloatField(), default=lambda: [0.0, 0.0])
    consignments = ReferenceField(Consignments, dbref=True)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            self.public_id = str(uuid.uuid4())
        # consignments = Consignments.objects(id_elemento=self.public_id).first()
        if self.source is None:
            self.source = init.AVAILABLE_SOURCES[0]

    def create_consignments_container(self):
        if self.consignments is None:
            # if there are not consignments then create a new document
            # relate an existing consignacion
            consignments = Consignments(id_elemento=self.public_id,
                                        elemento=self.to_summary())
            consignments.save()
            self.consignments = consignments

    def edit_leaf_component(self, new_internal: dict):
        try:

            to_update = ["name", "calculation_type"]
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

    def to_summary(self):
        return dict(public_id=self.public_id, name=self.name)

    def get_consignments(self):
        try:
            return Consignments.objects(id=self.consignments.id).first()
        except Exception as e:
            print(str(e))
            return None
