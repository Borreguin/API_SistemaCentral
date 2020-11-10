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


class ComponenteLeaf(EmbeddedDocument):
    public_id = StringField(required=True, default=None)
    name=StringField(required=True)
    source=StringField(choices=tuple(init.AVAILABLE_SOURCES))
    actualizado = DateTimeField(default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            #id = str(uuid.uuid4())
            self.public_id = str(uuid.uuid4())
        if self.source is None:
            self.source=init.AVAILABLE_SOURCES[0]
    #TODO: NO EXISTE ESTA FUNCION, NO EXISTEN CASOS QUE SE ADICIONEN LEAFS A LEAF
    def add_leaf_component(self,leaf_component:list):
        # check si todas los internal_component son de tipo ComponenteInternal
        check = [isinstance(t, ComponenteLeaf) for t in leaf_component]
        if not all(check):
            lg = [str(leaf_component[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes finales no es compatible:"] + lg

        # unificando las lista y crear una sola
        unique = dict()
        unified_list = self.leafs + leaf_component
        n_initial = len(self.leafs)
        n_total = len(unified_list)
        for u in unified_list:
            unique.update({u.public_id: u})
        self.internals = [unique[k] for k in unique.keys()]
        n_final = len(self.internals)
        return True, f"Componentes finales: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

    def edit_leaf_component(self,new_internal:dict):
        try:

            to_update = ["nombre", "tipo_calculo"]
            for key, value in new_internal.items():
                if key in to_update:
                    setattr(self, key, value)
            self.actualizado=dt.datetime.now()

            return True,f"Componente interno editado"

        except Exception as e:

            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc() #Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def __repr__(self):
        return f"<Internal {self.name},{len(self.internals)}>"

    def __str__(self):
        return f"<Internal {self.name},{len(self.internals)}>"

    def validate_leaf(self):
        return self.source is not None

