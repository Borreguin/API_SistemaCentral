"""
COMPONENT INTERNAL- BASE DE DATOS PARA SISTEMA CENTRAL
START DATE: 10/11/2020
DP V.2
"""

from dto.Classes.Operation import Operation
# from dto.mongo_engine_handler.Comp_Root import ComponenteRoot
from dto.mongo_engine_handler.Components.Comp_Leaf import *


class ComponenteInternal(EmbeddedDocument):
    public_id = StringField(required=True, default=None)
    document = StringField(required=False, default="ComponenteInternal")
    name = StringField(required=True)
    internals = EmbeddedDocumentListField('ComponenteInternal')
    leafs = ListField(EmbeddedDocumentField(ComponenteLeaf), required=True)
    calculation_type = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    position_x_y = ListField(FloatField(), default=lambda: [0.0, 0.0])
    updated = DateTimeField(default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            # id = str(uuid.uuid4())
            self.public_id = str(uuid.uuid4())
        if len(self.leafs) == 0:
            new_leaf = ComponenteLeaf(name=self.name)
            self.leafs = [new_leaf]
        if self.calculation_type is None:
            self.calculation_type = init.AVAILABLE_OPERATIONS[0]

    def check_loop(self):
        pass

    def change_internal_to_leaf(self):
        pass

    def add_internal_component(self, internal_component: list):
        # check si todas los internal_component son de tipo ComponenteInternal

        check = [isinstance(t, ComponenteInternal) for t in internal_component]
        if not all(check):
            lg = [str(internal_component[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de componentes internos no es compatible:"] + lg

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

    def add_leaf_component(self, leaf_component: list):
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
        self.leafs = [unique[k] for k in unique.keys()]
        n_final = len(self.leafs)
        self.delete_leaf(self.name)
        return True, f"Componentes finales: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

    def edit_internal_component(self, new_internal: dict):
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

    def __repr__(self):
        return f"<Internal {self.name},{len(self.internals)},{len(self.leafs)}>"

    def __str__(self):
        return f"<Internal {self.name},{len(self.internals)},{len(self.leafs)}>"
        # FUNCIONES DELETE

    def delete_internal(self, name_delete: str):
        new_internals = [e for e in self.internals if name_delete != e.name]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{name_delete}] en el componente interno [{self.name}]"
        self.internals = new_internals
        return True, "Componente interno eliminado"

    def delete_internal_by_id(self, id_internal: str):
        new_internals = [e for e in self.internals if id_internal != e.public_id]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{id_internal}] en el componente interno [{self.name}]"
        self.internals = new_internals
        return True, "Componente interno eliminado"

        # FUNCIONES DELETE

    def delete_leaf(self, name_delete: str):
        new_leaf = [e for e in self.leafs if name_delete != e.name]
        if len(new_leaf) == len(self.leafs):
            return False, f"No existe el componente final [{name_delete}] en el componente interno [{self.name}]"
        self.leafs = new_leaf
        if len(self.leafs) == 0:
            new_leaf = ComponenteLeaf(name=self.name)
            self.leafs = [new_leaf]
        return True, "Componente final eliminado"

    def delete_leaf_by_id(self, id_leaf: str):
        new_leaf = [e for e in self.leafs if id_leaf != e.public_id]
        if len(new_leaf) == len(self.leafs):
            return False, f"No existe el componente interno [{id_leaf}] en el componente root [{self.name}]"
        self.leafs = new_leaf
        if len(self.leafs) == 0:
            new_leaf = ComponenteLeaf(name=self.name)
            self.leafs = [new_leaf]
        return True, "Componente final eliminado"

        # FUNCIONES SEARCH

    def search_internal(self, internal_nombre: str):
        check = [i for i, e in enumerate(self.internals) if internal_nombre == e.name]
        if len(check) > 0:
            return True, self.internals[check[0]]
        elif len(self.internals) > 0:
            for internal in self.internals:
                return internal.search_internal_by_id(internal_nombre)
        else:
            return False, f"No existe el componente interno [{internal_nombre}] en el root [{self.name}]"

    def search_internal_by_id(self, id_internal: str):
        check = [i for i, e in enumerate(self.internals) if id_internal == e.public_id]
        if len(check) > 0:
            return True, self.internals[check[0]]
        elif len(self.internals) > 0:
            for internal in self.internals:
                return internal.search_internal_by_id(id_internal)
        else:
            return False, f"No existe el componente interno [{id_internal}] en el root [{self.name}]"

    # TODO: función recursiva
    def search_leaf(self, leaf_nombre: str):
        check = [i for i, e in enumerate(self.leafs) if leaf_nombre == e.name]
        if len(check) > 0:
            return True, self.leafs[check[0]]
        #Busqueda en siguientes niveles:
        elif len(self.internals)>0:
            for internal in self. internals:
                success,result=internal.search_leaf(leaf_nombre)
                if success:
                    return True, result
            return False,f"No existe el componente hoja con el nombre [{leaf_nombre}]"

        return False, f"No existe el componente [{leaf_nombre}] en el componente interno [{self.name}]"

    def search_leaf_by_id(self, id_leaf: str):
        # OPERACIÓN DE BUSQUEDA USANDO EL ATRIBUTO PUBLIC_ID
        check = [i for i, e in enumerate(self.leafs) if id_leaf == e.public_id]
        # Búsqueda en el primer nivel
        if len(check) > 0:
            # Si encuentra da la respuesta del primer nivel
            return True, self.leafs[check[0]]
        # Si no encuentra hace búsqueda en los siguientes niveles
        elif len(self.internals) > 0:
            for internal in self.internals:
                success, result = internal.search_leaf_by_id(id_leaf)
                if success:
                    return True, result
            return False, f"No existe la hoja con el id [{id_leaf}]"

        return False, f"No existe la hoja con el id [{id_leaf}]"

    def change_leaf_to_internal(self, leaf_id: str, leafs: list):
        # check si todas las leafs son de tipo Componente Leaf
        check = [isinstance(t, ComponenteLeaf) for t in leafs]
        if not all(check):
            lg = [str(leafs[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de leafs no es compatible:"] + lg
        success, leaf = self.search_leaf_by_id(leaf_id)
        if success:
            if len(leafs) < 2:  # Restriccion 2 leafs al menos
                return False, None, "Para realizar esta operación se requieren al menos 2 componentes"
            new_internal_component = ComponenteInternal(public_id=leaf.public_id, name=leaf.name, leafs=leafs)
            self.delete_leaf_by_id(leaf_id)
            self.add_internal_component([new_internal_component])
            return True, new_internal_component, "Operación existosa"

    # TODO: VALIDAR TIPO DE CALCULO
    def validate_internal(self):
        is_ok = True
        for leaf in self.leafs:  # VALIDAR FUENTE
            is_ok = leaf.validate_leaf() and is_ok
        for internal in self.internals:
            is_ok = internal.validate_internal() and is_ok
        return is_ok

    def search_parent_of(self, id_internal: str):
        check = [i for i, e in enumerate(self.internals) if
                 id_internal == e.public_id]  # BUSCA INTERNALS DEL PRIMER NIVEL
        if len(check) > 0:
            return True, self
        elif len(self.internals) > 0:
            for internal in self.internals:
                success, result = internal.search_parent_of(id_internal)
                if success:
                    return True, result
        else:
            return False, f"No existe padre del componente interno [{id_internal}]"

    def add_operations(self, to_add_operations: dict):
        operating_list = [internal.public_id for internal in self.internals]
        operating_list=operating_list+([leaf.public_id for leaf in self.leafs])
        print(operating_list)
        success, msg = Operation(topology=to_add_operations, operating_list=operating_list).validate_operations()
        if success:
            self.topology = to_add_operations
        return success, msg

    def to_dict(self):
        return dict(public_id=self.public_id, name=self.name, internals=[i.to_dict() for i in self.internals],
                    leafs=[l.to_dict() for l in self.leafs], position_x_y=self.position_x_y)

    def update_position_x_y(self, pos_x: float, pos_y: float):
        self.position_x_y = [pos_x, pos_y]