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
    name = StringField(required=True)
    calculation_type = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    position_x_y = ListField(FloatField(), default=lambda: [0.0, 0.0])
    updated = DateTimeField(default=dt.datetime.now())
    #REFERENCIA COMPONENTE ROOT
    comp_roots=ListField(ReferenceField(ComponenteRoot,dbref=True), default=[])
    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            self.public_id = str(uuid.uuid4())
        if self.calculation_type is None:
            self.calculation_type=init.AVAILABLE_OPERATIONS[0]



    def add_root_component(self,root_component:list):
        # check si todas los root_component son de tipo ComponenteRoot
        check = [isinstance(t, ComponenteRoot) for t in root_component]
        if not all(check):
            lg = [str(root_component[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes root no es compatible:"] + lg

        # unificando las lista y crear una sola
        unified_list = self.comp_roots + root_component
        n_initial = len(self.comp_roots)
        n_total = len(unified_list)
        self.comp_roots=unified_list
        n_final=len(self.comp_roots)
        return True, f"Componentes root: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"


    def delete_root_component(self,root_component:list):
        # check si todas los root_component son de tipo ComponenteRoot
        check = [isinstance(t, ComponenteRoot) for t in root_component]
        if not all(check):
            lg = [str(root_component[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes root no es compatible:"] + lg
        if len(self.comp_roots)==0:
            return False, [f"La lista de componentes root esta vacia"]
        for comp in self.comp_roots:
            for root in root_component:
                if comp==root:
                    self.comp_roots.remove(root)
                    return True,f'Elemento {root} eliminado'
        return False

    def edit_leaf_block(self,new_leaf_block:dict):
        try:
            to_update = ["name", "calculation_type"]
            for key, value in new_leaf_block.items():
                if key in to_update:
                    setattr(self, key, value)
            self.updated = dt.datetime.now()
            return True, f"Bloque leaf editado"
        except Exception as e:
            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc()  # Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def update_position_x_y(self, pos_x: float, pos_y: float):
        self.position_x_y = [pos_x, pos_y]

    def __repr__(self):
        return f"<Bloque Leaf {self.name},{self.root_id}>"

    def __str__(self):
        return f"<Bloque Leaf {self.name},{self.root_id}>"

    def validate_bloque_leaf(self):
        return self.calculation_type is not None

    def to_dict(self):
        root_to_dict=[]
        for comp in self.comp_roots:
            if hasattr(comp,"name"):
                root_to_dict.append(comp.to_dict())
        return dict(name=self.name, calculation_type=self.calculation_type, position_x_y=self.position_x_y,
                    comp_roots=root_to_dict)
