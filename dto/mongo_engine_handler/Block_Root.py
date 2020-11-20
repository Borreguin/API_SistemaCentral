"""
BLOQUE ROOT- BASE DE DATOS PARA SISTEMA CENTRAL
START DATE: 12/11/2020
DP V.1
"""
import hashlib
import traceback
from dto.mongo_engine_handler import log
from mongoengine import *
import datetime as dt
import uuid

from dto.mongo_engine_handler.Block_Leaf import *
from settings import initial_settings as init
from dto.mongo_engine_handler.Comp_Internal import ComponenteInternal
from dto.mongo_engine_handler.Comp_Leaf import ComponenteLeaf

class BloqueRoot(Document):
    public_id=StringField(required=True, default=None)
    nombre = StringField(required=True)
    tipo_calculo = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    actualizado = DateTimeField(default=dt.datetime.now())
    block_leafs = ListField(EmbeddedDocumentField(BloqueLeaf), required=True)
    document = StringField(required=True, default="BloqueRoot")
    unique=StringField(required=True, unique=True)
    meta = {"collection": "CONFG|Bloques"}


    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.public_id is None:
            self.public_id = str(uuid.uuid4())
        if len(self.block_leafs)==0:
           new_block_leaf=BloqueLeaf(name=self.nombre,tipo_calculo="LEAF")
           self.block_leafs=[new_block_leaf]
        if self.tipo_calculo is None:
            self.tipo_calculo=init.AVAILABLE_OPERATIONS[0]
        if self.unique is None:
            self.unique=str(self.nombre).lower()

    def add_leaf_block(self,leaf_block:list):
        # check si todas los leaf_block son de tipo ComponenteInternal
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
            unique.update({u.public_id: u})
        self.block_leafs = [unique[k] for k in unique.keys()]
        n_final = len(self.block_leafs)
        self.delete_leaf(self.nombre)
        return True, f"Bloques: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

    # TODO: Root to internal (Funcion de bloque??)
    def change_root_to_internal(self,root):
        pass

    def edit_root_block(self,new_root:dict):
        try:

            to_update = ["nombre", "tipo_calculo"]
            for key, value in new_root.items():
                if key in to_update:
                    setattr(self, key, value)
            self.actualizado=dt.datetime.now()

            return True,f"Bloque Root editado"

        except Exception as e:

            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc() #Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def __repr__(self):
        return f"<Bloque Root {self.nombre},{len(self.block_leafs)}>"

    def __str__(self):
        return f"<Bloque Root {self.nombre},{len(self.block_leafs)}>"

    #FUNCIONES DELETE

    def delete_leaf(self, name_delete:str):
        new_block_leafs = [e for e in self.block_leafs if name_delete != e.name]
        if len(new_block_leafs) == len(self.block_leafs):
            return False, f"No existe el bloque [{name_delete}] en el bloque root [{self.nombre}]"
        self.block_leafs = new_block_leafs
        if len(self.block_leafs) == 0:
            new_block_leafs = BloqueLeaf(name=self.nombre, tipo_calculo="LEAF")
            self.block_leafs = [new_block_leafs]
        return True, "Bloque leaf eliminado"

    def delete_leaf_by_id(self, id_leaf:str):
        new_block_leafs = [e for e in self.block_leafs if id_leaf != e.public_id]
        if len(new_block_leafs) == len(self.block_leafs):
            return False, f"No existe el bloque [{id_leaf}] en el bloque root [{self.nombre}]"
        self.block_leafs = new_block_leafs
        if len(self.block_leafs) == 0:
            new_block_leafs = BloqueLeaf(name=self.nombre, tipo_calculo="LEAF")
            self.block_leafs = [new_block_leafs]
        return True, "Bloque leaf eliminado"


    #TODO: REVISAR FUNCION SI ES NECESARIO
    def delete_all(self): #REVISAR FUNCION
        pass
        # for e in self.block_leafs:
          #  self.delete()

    # FUNCIONES SEARCH

    def search_leaf(self, leaf_nombre: str):
        check = [i for i, e in enumerate(self.block_leafs) if leaf_nombre == e.name]
        if len(check) > 0:
            return True, self.block_leafs[check[0]]
        elif len(self.block_leafs) > 0:
            for internal in self.block_leafs:
                success, result = internal.search_leaf(leaf_nombre)
                if success:
                    return success, result
        else:
            return False, f"No existe el bloque [{leaf_nombre}] en el bloque root [{self.nombre}]"

    def search_leaf_by_id(self, id_leaf: str):
        check = [i for i, e in enumerate(self.block_leafs) if id_leaf == e.public_id]
        if len(check) > 0:
            return True, self.block_leafs[check[0]]
        elif len(self.block_leafs) > 0:
            for internal in self.block_leafs:
                success,result= internal.search_leaf_by_id(id_leaf)
                #print(self.nombre,internal.name,success,result)
                if success:
                    return success,result
        else:
            return False, f"No existe el bloque [{id_leaf}] en el bloque root [{self.nombre}]"


    #TODO: EXISTE FUNCIÓN CAMBIAR BLOQUE LEAF A BLOQUE ROOT?
    def change_internal_to_root(self,internal_id:str, internal: list, bloque:str):
        # check si todas los componentes internos son de tipo ComponenteInternal
        check = [isinstance(t, ComponenteInternal) for t in internal]
        if not all(check):
            lg = [str(internal[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de block_leafs no es compatible:"] + lg

        success, internal_old=self.search_internal_by_id(internal_id)
        if success:
            new_root_component = ComponenteRoot(public_id=internal_old.public_id, nombre=internal_old.name,\
                                                block_leafs=internal,bloque=bloque)
            self.delete_internal_by_id(internal_id)

            check = [i for i, e in enumerate(internal)]
            if len(check) > 0:
                for i in range(len(internal)):
                    a=internal[i-1].name
                    self.delete_internal(internal[i-1].name)
            new_root_component.save() #ERROR DE ID
            return True,new_root_component,"Operación existosa"

    def validate_root(self):
        is_ok=True
        for leaf in self.block_leafs:
            is_ok=leaf.validate_bloque_leaf() and is_ok
        return is_ok

    def search_parent_of(self, id_leaf: str):
        check = [i for i, e in enumerate(self.block_leafs) if id_leaf == e.public_id] #BUSCA block_leafs DEL PRIMER NIVEL
        if len(check) > 0:
            return True, self
        else:
            return False, f"No existe padre del bloque leaf [{id_leaf}]"

    def to_dict(self):
        return dict(nombre=self.nombre, block_leafs=[i.to_dict() for i in self.block_leafs])
