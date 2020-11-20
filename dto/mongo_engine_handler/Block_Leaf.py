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
from dto.mongo_engine_handler.Comp_Root import *


class BloqueLeaf(EmbeddedDocument):
    public_id = StringField(required=True, default=None)
    name=StringField(required=True)
    #root_id=ListField(required=True, default=None) #Lista de componentes root que conforman el bloque leaf
    tipo_calculo = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    actualizado = DateTimeField(default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            self.public_id = str(uuid.uuid4())
        if self.tipo_calculo is None:
            self.tipo_calculo=init.AVAILABLE_OPERATIONS[0]


    # TODO: VALIDAR SI SE REQUIERE FUNCION PARA ADICIONAR COMPONENTES ROOT AL BLOQUE LEAF
    def add_root_component(self,root_component:list):
        # check si todas los root_component son de tipo ComponenteRoot
        check = [isinstance(t, ComponenteRoot) for t in root_component]
        if not all(check):
            lg = [str(root_component[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes root no es compatible:"] + lg

        # unificando las lista y crear una sola
        unique = dict()
        unified_list = self.root_id + root_component
        n_initial = len(self.root_id)
        n_total = len(unified_list)
        for u in unified_list:
            unique.update({u.public_id: u})
        self.root_id = [unique[k] for k in unique.keys()]
        n_final = len(self.root_id)
        return True, f"Componentes root: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

    def edit_leaf_block(self,new_leaf_block:dict):
        try:

            to_update = ["name", "tipo_calculo"]
            for key, value in new_leaf_block.items():
                if key in to_update:
                    setattr(self, key, value)
            self.actualizado=dt.datetime.now()

            return True,f"Bloque leaf editado"

        except Exception as e:

            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc() #Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def __repr__(self):
        return f"<Bloque Leaf {self.name},{self.root_id}>"

    def __str__(self):
        return f"<Bloque Leaf {self.name},{self.root_id}>"

    def validate_bloque_leaf(self):
        return self.tipo_calculo is not None

    def to_dict(self):
        return dict(name=self.name, tipo_calculo=self.tipo_calculo)