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
    public_id = StringField(required=True, unique=True, default=None)
    name=StringField(required=True)
    sources=StringField(choices=tuple(init.AVAILABLE_SOURCES))
    actualizado = DateTimeField(default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            #id = str(uuid.uuid4())
            self.public_id = str(uuid.uuid4())
        if self.sources is None:
            self.sources=init.AVAILABLE_SOURCES[0]

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
        return f"<Internal {self.name},{len(self.internals)},{len(self.leafs)}>"




class ComponenteInternal(EmbeddedDocument):
    public_id=StringField(required=True, unique=True, default=None)
    name=StringField(required=True)
    internals=EmbeddedDocumentListField('ComponenteInternal')
    leafs=ListField(EmbeddedDocumentField(ComponenteLeaf), required=True)
    tipo_calculo = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    actualizado = DateTimeField(default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            #id = str(uuid.uuid4())
            self.public_id = str(uuid.uuid4())
        if len(self.leafs) ==0:
            new_leaf=ComponenteLeaf(name=self.name)
            self.leafs=[new_leaf]
        if self.tipo_calculo is None:
            self.tipo_calculo = init.AVAILABLE_OPERATIONS[0]
    def check_loop(self):
        pass
    def change_internal_to_leaf(self):
        pass

    def add_internal_component(self,internal_component:list):
        # check si todas los internal_component son de tipo ComponenteInternal

        check = [isinstance(t, ComponenteInternal) for t in internal_component]
        if not all(check):
            lg = [str(internal_component[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes internos no es compatible:"] + lg

        self.delete_leaf(self.name)


        # unificando las lista y crear una sola
        unique = dict()
        unified_list = self.internals + internal_component
        n_initial = len(self.internals)
        n_total = len(unified_list)
        for u in unified_list:
            unique.update({u.public_id: u})
        self.internals = [unique[k] for k in unique.keys()]
        n_final = len(self.internals)
        return True, f"Componentes internos: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

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

    def edit_internal_component(self,new_internal:dict):
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
        return f"<Internal {self.name},{len(self.internals)},{len(self.leafs)}>"

        # FUNCIONES DELETE

    def delete_internal(self, name_delete:str):
        new_internals = [e for e in self.internals if name_delete != e.name]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{name_delete}] en el componente interno [{self.name}]"
        self.internals = new_internals
        return True, "Componente interno eliminado"

    def delete_internal_by_id(self, id_internal:str):
        new_internals = [e for e in self.internals if id_internal != e.public_id]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{id_internal}] en el componente interno [{self.name}]"
        self.internals = new_internals
        return True, "Componente interno eliminado"

        # FUNCIONES DELETE

    def delete_leaf(self, name_delete:str):
        new_leaf = [e for e in self.leafs if name_delete != e.name]
        if len(new_leaf) == len(self.leafs):
            return False, f"No existe el componente final [{name_delete}] en el componente interno [{self.name}]"
        self.leafs = new_leaf
        return True, "Componente final eliminado"

    def delete_leaf_by_id(self, id_leaf:str):
        new_leaf = [e for e in self.leafs if id_leaf != e.public_id]
        if len(new_leaf) == len(self.leafs):
            return False, f"No existe el componente interno [{id_leaf}] en el componente root [{self.nombre}]"
        self.leafs = new_leaf
        return True, "Componente final eliminado"


        # FUNCIONES SEARCH

    def search_internal(self, internal_nombre: str):
        check = [i for i, e in enumerate(self.internals) if internal_nombre == e.name]
        if len(check) > 0:
            return True, self.internals[check[0]]
        return False, f"No existe el componente interno [{internal_nombre}] en el root [{self.name}]"

    def search_internal_by_id(self, id_internal: str):
        check = [i for i, e in enumerate(self.internals) if id_internal == e.public_id]
        if len(check) > 0:
            return True, self.internals[check[0]]
        return False, f"No existe el componente interno [{id_internal}] en el root [{self.name}]"

    def search_leaf(self, leaf_nombre: str):
        check = [i for i, e in enumerate(self.leafs) if leaf_nombre == e.name]
        if len(check) > 0:
            return True, self.leafs[check[0]]
        return False, f"No existe el componente final [{leaf_nombre}] en el componente interno [{self.name}]"

    def search_leaf_by_id(self, id_leaf: str):
        # OPERACIÓN DE BUSQUEDA USANDO EL ATRIBUTO PUBLIC_ID
        check = [i for i, e in enumerate(self.leafs) if id_leaf == e.public_id]
        if len(check) > 0:
            return True, self.leafs[check[0]] #PRIMER ELEMENTO QUE ENCONTRO --> EN LEAFS
        return False, f"No existe el componente final [{id_leaf}] en el componente interno [{self.name}]"

    # TODO: leaf to internal (Revisar)
    def change_leaf_to_internal(self,leaf_id:str, leafs: list):
        success, leaf=self.search_leaf_by_id(leaf_id)
        if success:
            if len(leafs) < 2:  # Restriccion 2 leafs al menos
                return False, None, "Para realizar esta operación se requieren al menos 2 componentes"
            new_internal_component = ComponenteInternal(public_id=leaf.public_id, name=leaf.name, leafs=leafs)
            self.delete_leaf_by_id(leaf_id)
            self.add_internal_component([new_internal_component])

            return True,new_internal_component,"Operación existosa"



class ComponenteRoot(Document):
    public_id=StringField(required=True, unique=True, default=None)
    bloque = StringField(required=True)
    nombre = StringField(required=True)
    tipo_calculo = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    actualizado = DateTimeField(default=dt.datetime.now())
    internals = ListField(EmbeddedDocumentField(ComponenteInternal), required=True)
    document = StringField(required=True, default="ComponenteRoot")
    unique=StringField(required=True, unique=True)
    meta = {"collection": "CONFG|componentes"}


    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.public_id is None:
            #id = str(uuid.uuid4())
            self.public_id = str(uuid.uuid4())
        if len(self.internals)==0:
           new_component_internal=ComponenteInternal(name=self.nombre,internals=[],leafs=[],tipo_calculo="LEAF")
           self.internals=[new_component_internal]
        if self.tipo_calculo is None:
            self.tipo_calculo=init.AVAILABLE_OPERATIONS[0]
        if self.unique is None:
            self.unique=str(self.bloque).lower()+"_"+str(self.nombre).lower()

    def add_internal_component(self,internal_component:list):
        # check si todas los internal_component son de tipo ComponenteInternal
        check = [isinstance(t, ComponenteInternal) for t in internal_component]
        if not all(check):
            lg = [str(internal_component[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes internos no es compatible:"] + lg

        self.delete_internal(self.nombre)

        # unificando las lista y crear una sola
        unique = dict()
        unified_list = self.internals + internal_component
        n_initial = len(self.internals)
        n_total = len(unified_list)
        for u in unified_list:
            unique.update({u.public_id: u})
        self.internals = [unique[k] for k in unique.keys()]
        n_final = len(self.internals)
        return True, f"Componentes internos: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

    # TODO: Root to internal (Revisar)
    def change_root_to_internal(self,root):
        self.add_internal_component([self.nombre])
        new_root = ComponenteRoot(nombre=root)



        pass

    def edit_root_component(self,new_root:dict):
        try:

            to_update = ["bloque", "nombre", "tipo_calculo"]
            for key, value in new_root.items():
                if key in to_update:
                    setattr(self, key, value)
            self.actualizado=dt.datetime.now()

            return True,f"Root editado"

        except Exception as e:

            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc() #Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def __repr__(self):
        return f"<Root {self.bloque},{self.nombre},{len(self.internals)}>"

    #FUNCIONES DELETE

    def delete_internal(self, name_delete:str):
        if len(self.internals)==1:
            new_internals = [e for e in self.internals if name_delete != e.name]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{name_delete}] en el componente root [{self.nombre}]"
        self.internals = new_internals
        return True, "Componente interno eliminado"

    def delete_internal_by_id(self, id_internal:str):
        new_internals = [e for e in self.internals if id_internal != e.public_id]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{id_internal}] en el componente root [{self.nombre}]"
        self.internals = new_internals
        return True, "Componente interno eliminado"
    #TODO: REVISAR FUNCION SI ES NECESARIO
    def delete_all(self): #REVISAR FUNCION
        pass
        # for e in self.internals:
          #  self.delete()

    # FUNCIONES SEARCH

    def search_internal(self, internal_nombre: str):
        check = [i for i, e in enumerate(self.internals) if internal_nombre == e.name]
        if len(check) > 0:
            return True, self.internals[check[0]]
        return False, f"No existe el componente interno [{internal_nombre}] en el root [{self.nombre}]"

    def search_internal_by_id(self, id_internal: str):
        check = [i for i, e in enumerate(self.internals) if id_internal == e.public_id]
        if len(check) > 0:
            return True, self.internals[check[0]]
        return False, f"No existe el componente interno [{id_internal}] en el root [{self.nombre}]"

