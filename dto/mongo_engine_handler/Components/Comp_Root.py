"""
COMPONENT ROOT- BASE DE DATOS PARA SISTEMA CENTRAL
START DATE: 10/11/2020
DP V.2
"""

from dto.mongo_engine_handler.Components.Comp_Internal import *
from dto.mongo_engine_handler.Components.Comp_Leaf import *


class ComponenteRoot(Document):
    public_id = StringField(required=True, default=None)
    block = StringField(required=True)
    name = StringField(required=True)
    calculation_type = StringField(choices=tuple(init.AVAILABLE_OPERATIONS))
    updated = DateTimeField(default=dt.datetime.now())
    internals = ListField(EmbeddedDocumentField(ComponenteInternal), required=True)
    document = StringField(required=True, default="ComponenteRoot")
    unique = StringField(required=True, unique=True)
    position_x_y = ListField(FloatField(), default=lambda: [0.0, 0.0])
    topology = DictField(required=False, default=dict())
    meta = {"collection": "CONFG|Components"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.public_id is None:
            # id = str(uuid.uuid4())
            self.public_id = str(uuid.uuid4())
        if len(self.internals) == 0:
            new_component_internal = ComponenteInternal(name=self.name, internals=[], leafs=[], calculation_type="LEAF")
            self.internals = [new_component_internal]
        if self.calculation_type is None:
            self.calculation_type = init.AVAILABLE_OPERATIONS[0]
        if self.unique is None:
            self.unique = str(self.block).lower() + "_" + str(self.name).lower()

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
        self.delete_internal(self.name)
        return True, f"Componentes internos: -remplazados: [{n_total - n_final}] -añadidos: [{n_final - n_initial}]"

    # TODO: Root to internal (Eliminar- Funcion de bloque)
    def change_root_to_internal(self, root):
        pass

    def edit_root_component(self, new_root: dict):
        try:
            to_update = ["block", "name", "calculation_type"]
            for key, value in new_root.items():
                if key in to_update:
                    setattr(self, key, value)
            self.updated = dt.datetime.now()
            return True, f"Root editado"
        except Exception as e:
            msg = f"Error al actualizar {self}​​: {str(e)}​​"
            tb = traceback.format_exc()  # Registra últimos pasos antes del error
            log.error(f"{msg}​​ \n {tb}​​")
            return False, msg

    def __repr__(self):
        return f"<Root {self.block},{self.name},{len(self.internals)}>"

    def __str__(self):
        return f"<Root {self.block},{self.name},{len(self.internals)}>"

    # FUNCIONES DELETE

    def delete_internal(self, name_delete: str):
        new_internals = [e for e in self.internals if name_delete != e.name]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{name_delete}] en el componente root [{self.name}]"
        self.internals = new_internals
        if len(self.internals) == 0:
            new_component_internal = ComponenteInternal(name=self.name, internals=[], leafs=[], calculation_type="LEAF")
            self.internals = [new_component_internal]
        return True, "Componente interno eliminado"

    def delete_internal_by_id(self, id_internal: str):
        new_internals = [e for e in self.internals if id_internal != e.public_id]
        if len(new_internals) == len(self.internals):
            return False, f"No existe el componente interno [{id_internal}] en el componente root [{self.name}]"
        self.internals = new_internals
        if len(self.internals) == 0:
            new_component_internal = ComponenteInternal(name=self.name, internals=[], leafs=[], calculation_type="LEAF")
            self.internals = [new_component_internal]
        return True, "Componente interno eliminado"

    # FUNCIONES SEARCH
    def search_internal(self, internal_nombre: str):
        check = [i for i, e in enumerate(self.internals) if internal_nombre == e.name]
        if len(check) > 0:
            return True, self.internals[check[0]]
        elif len(self.internals) > 0:
            for internal in self.internals:
                success, result = internal.search_internal(internal_nombre)
                if success:
                    return success, result
        else:
            return False, f"No existe el componente interno [{internal_nombre}] en el root [{self.name}]"

    def search_internal_by_id(self, id_internal: str):
        check = [i for i, e in enumerate(self.internals) if id_internal == e.public_id]
        if len(check) > 0:
            return True, self.internals[check[0]]
        elif len(self.internals) > 0:
            for internal in self.internals:
                success, result = internal.search_internal_by_id(id_internal)
                # print(self.nombre,internal.name,success,result)
                if success:
                    return success, result
            return False, f"No existe el componente interno [{id_internal}] en el root [{self.name}]"
        else:
            return False, f"No existe el componente interno [{id_internal}] en el root [{self.name}]"

    # CHANGE INTERNAL TO LEAF

    def change_internal_to_leaf(self, internal_id: str):
        check = [i for i, e in enumerate(self.internals) if internal_id == e.public_id]
        if len(check) > 0:
            return False, None, f"No se puede realizar la operacion al internal [{internal_id}]"
        elif len(self.internals) > 0:
            for internal in self.internals:
                success, result = internal.search_internal_by_id(internal_id)
                if success:
                    new_leaf_component = ComponenteLeaf(public_id=result.public_id, name=result.name)
                    # Encontrar internal padre y añadir new_leaf_component
                    success, parent = self.search_parent_of(internal_id)
                    if success:
                        parent.delete_internal_by_id(internal_id)
                        parent.add_leaf_component([new_leaf_component])
                        return True, new_leaf_component, "Operación existosa"
        return False, None, "No se pudo convertir internal a leaf"

    # TODO: ADD ROOT IN BLOQUE ? ERROR LINEA 388
    def change_internal_to_root(self, internal_id: str, internal: list, bloque: str):
        # check si todas los componentes internos son de tipo ComponenteInternal
        check = [isinstance(t, ComponenteInternal) for t in internal]
        if not all(check):
            lg = [str(internal[i]) for i, v in enumerate(check) if not v]
            return False, [f"La siguiente lista de internals no es compatible:"] + lg

        success, internal_old = self.search_internal_by_id(internal_id)
        if success:
            new_root_component = ComponenteRoot(public_id=internal_old.public_id, nombre=internal_old.name, \
                                                internals=internal, bloque=bloque)
            self.delete_internal_by_id(internal_id)

            check = [i for i, e in enumerate(internal)]
            if len(check) > 0:
                for i in range(len(internal)):
                    a = internal[i - 1].name
                    self.delete_internal(internal[i - 1].name)
            new_root_component.save()  # ERROR DE ID
            return True, new_root_component, "Operación existosa"

    def validate_root(self):
        is_ok = True
        for internal in self.internals:
            is_ok = internal.validate_internal() and is_ok
        return is_ok

    def search_parent_of(self, id_internal: str):
        # BUSCA INTERNALS DEL PRIMER NIVEL
        check = [i for i, e in enumerate(self.internals) if id_internal == e.public_id]
        if len(check) > 0:
            return True, self
        elif len(self.internals) > 0:
            for internal in self.internals:
                success, result = internal.search_parent_of(id_internal)
                if success:
                    return True, result
        else:
            return False, f"No existe padre del componente interno [{id_internal}]"

    def search_leaf_by_id(self, id_leaf):
        # Encuentra de manera recursiva una hoja dentro de cualquier internal existente
        for internal in self.internals:
            success, result = internal.search_leaf_by_id(id_leaf)
            if success:
                return True, result
        return False, f"No se encontró la hoja con el id {id_leaf}"

    # TODO: revisado
    def add_operations(self, to_add_operations: dict):
        # El diccionario de topologia es ingrsado mediante la interfaz gráfica
        operating_list = [internal.public_id for internal in self.internals]
        print(operating_list)
        success, msg = Topology(topology=to_add_operations, operating_list=operating_list).validate_operations()
        if success:
            self.topology = to_add_operations
        return success, msg

    def to_dict(self):
        return dict(document=self.document, public_id=self.public_id, bloque=self.block, name=self.name,
                    internals=[i.to_dict() for i in self.internals], position_x_y=self.position_x_y)

    def update_position_x_y(self, pos_x: float, pos_y: float):
        self.position_x_y = [pos_x, pos_y]