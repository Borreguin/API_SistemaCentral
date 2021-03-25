"""
BLOQUE ROOT- BASE DE DATOS PARA SISTEMA CENTRAL
START DATE: 12/11/2020
DP V.1
"""
import hashlib
import traceback

from dto.Classes.Operation import Operation
from dto.mongo_engine_handler import log
from mongoengine import *
import datetime as dt
import uuid

from dto.mongo_engine_handler.Block_Leaf import *
from settings import initial_settings as init
from dto.mongo_engine_handler.Comp_Internal import ComponenteInternal
from dto.mongo_engine_handler.Comp_Leaf import ComponenteLeaf


class OperationBlock(EmbeddedDocument):
    public_id = StringField(required=True, default=None)
    operation_type = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    operator_ids = ListField(StringField(), default=[], required=True)
    parameters = DictField(required=False)
    position_x_y = ListField(FloatField(), default=lambda: [0.0, 0.0])


class BloqueRoot(Document):
    public_id = StringField(required=True, default=None)
    name = StringField(required=True, unique=True)
    calculation_type = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    updated = DateTimeField(default=dt.datetime.now())
    block_leafs = ListField(EmbeddedDocumentField(BloqueLeaf), default=[])
    document = StringField(required=True, default="BloqueRoot")
    topology = DictField(required=False, default=dict())
    unique = StringField(required=True, unique=True)
    position_x_y = ListField(FloatField(), default=lambda: [0.0, 0.0])
    operation_blocks = ListField(OperationBlock, required=False)
    meta = {"collection": "CONFG|Bloques"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.public_id is None:
            self.public_id = str(uuid.uuid4())
        if self.calculation_type is None:
            self.calculation_type = init.AVAILABLE_OPERATIONS[1]
        if self.unique is None:
            self.unique = str(self.name).lower()

    def add_and_replace_leaf_block(self, leaf_block: list):
        # Esta función añade nuevos leafs blocks, en caso que ya exista el bloque leaf este es reemplazado
        # check si todas los root_component_list son de tipo ComponenteInternal
        check = [isinstance(t, BloqueLeaf) for t in leaf_block]
        if not all(check):
            lg = [str(leaf_block[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes internos no es compatible:"] + lg
        # unificando las lista y crear una sola
        unique = dict()
        unified_list = self.block_leafs + leaf_block
        n_initial = len(self.block_leafs)
        n_total = len(unified_list)
        for u in unified_list:
            unique.update({str(u.name).lower(): u})
        self.block_leafs = [unique[k] for k in unique.keys()]
        n_final = len(self.block_leafs)
        self.delete_leaf(self.name)
        return True, f"Bloques: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

    def add_new_leaf_block(self, leaf_block_list: list):
        # Añade solamente aquellos que son nuevos
        # check si todas los root_component_list son de tipo ComponenteInternal
        check = [isinstance(t, BloqueLeaf) for t in leaf_block_list]
        if not all(check):
            lg = [str(leaf_block_list[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de bloques internos no es compatible:"] + lg
        # unificando las lista y crear una sola
        new_leafs = list()
        for n_leaf in leaf_block_list:
            not_found = True
            for b_leaf in self.block_leafs:
                if str(n_leaf.name).lower().strip() == str(b_leaf.name).lower().strip():
                    not_found = False
            if not_found:
                new_leafs.append(n_leaf)

        success = len(new_leafs) > 0
        if success:
            self.block_leafs += new_leafs
            self.block_leafs.sort(key=lambda x: x.name)
        msg = "El bloque ya existe" if len(leaf_block_list) == 1 else "Los bloques ya existen"
        return success, f"Bloques añadidos: [{len(new_leafs)}]" if success else msg

    # TODO: Root to internal (Funcion de bloque??)
    def change_root_to_internal(self, root):
        pass

    # Funciones para editar
    def edit_root_block(self, new_root: dict):
        try:
            to_update = ["name", "calculation_type"]
            for key, value in new_root.items():
                if key in to_update:
                    setattr(self, key, value)
            self.updated = dt.datetime.now()

            return True, f"Bloque Root editado"

        except Exception as e:

            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc()  # Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def edit_leaf_by_id(self, public_id: str, new_leaf: dict):
        check = [i for i, e in enumerate(self.block_leafs) if public_id == e.public_id]
        if len(check) == 0:
            return False, None, "No encontró bloque leaf asociado a este Id público"
        try:
            success, msg = self.block_leafs[check[0]].edit_leaf_block(new_leaf)
            if success:
                for comp in self.block_leafs[check[0]].comp_roots:
                    comp.block = self.block_leafs[check[0]].name
                return success, self.block_leafs[check[0]], msg
            return False, None, msg
        except Exception as e:
            return False, None, f"Ocurrió un problema al actualizar el bloque leaf. {str(e)}"

    def __repr__(self):
        return f"<Bloque Root {self.name},{len(self.block_leafs)}>"

    def __str__(self):
        return f"<Bloque Root {self.name},{len(self.block_leafs)}>"

    def update_position_x_y(self, pos_x: float, pos_y: float):
        self.position_x_y = [pos_x, pos_y]

    # FUNCIONES DELETE

    def delete_leaf(self, name_delete: str):
        new_block_leafs = [e for e in self.block_leafs if name_delete != e.name]
        if len(new_block_leafs) == len(self.block_leafs):
            return False, f"No existe el bloque [{name_delete}] en el bloque root [{self.name}]"
        self.block_leafs = new_block_leafs
        if len(self.block_leafs) == 0:
            new_block_leafs = BloqueLeaf(name=self.name, calculation_type="LEAF")
            self.block_leafs = [new_block_leafs]
        return True, "Bloque leaf eliminado"

    def delete_leaf_by_id(self, id_leaf: str):
        new_block_leafs = [e for e in self.block_leafs if id_leaf != e.public_id]
        if len(new_block_leafs) == len(self.block_leafs):
            return False, f"No existe el bloque [{id_leaf}] en el bloque root [{self.name}]"
        self.block_leafs = new_block_leafs
        # Cuando se elimina un bloque interno, no importa si este queda vacío.
        return True, "Bloque leaf eliminado"

    # FUNCIONES SEARCH

    def search_leaf(self, leaf_nombre: str):
        check = [i for i, e in enumerate(self.block_leafs) if leaf_nombre == e.name]
        if len(check) > 0:
            return True, self.block_leafs[check[0]]
        else:
            return False, f"No existe el bloque [{leaf_nombre}] en el bloque root [{self.name}]"

    def search_leaf_by_id(self, id_leaf: str):
        check = [i for i, e in enumerate(self.block_leafs) if id_leaf == e.public_id]
        if len(check) > 0:
            return True, self.block_leafs[check[0]]
        # un bloque root solo tiene hojas, no hay necesidad de buscar recursivamente
        else:
            return False, f"No existe el bloque [{id_leaf}] en el bloque root [{self.name}]"

    def add_operations(self, to_add_operations: dict):
        operating_list = [leaf.public_id for leaf in self.block_leafs]
        print(operating_list)
        success, msg = Operation(topology=to_add_operations, operating_list=operating_list).validate_operations()
        if success:
            self.topology = to_add_operations
        return success, msg

    def validate_root(self):
        is_ok = True
        for leaf in self.block_leafs:
            is_ok = leaf.validate_bloque_leaf() and is_ok
        return is_ok

    def search_parent_of(self, id_leaf: str):
        check = [i for i, e in enumerate(self.block_leafs) if
                 id_leaf == e.public_id]  # BUSCA block_leafs DEL PRIMER NIVEL
        if len(check) > 0:
            return True, self
        else:
            return False, f"No existe padre del bloque leaf [{id_leaf}]"

    def to_dict(self):
        return dict(document=self.document, public_id=self.public_id, name=self.name,
                    block_leafs=[i.to_dict() for i in self.block_leafs], position_x_y=self.position_x_y, )
