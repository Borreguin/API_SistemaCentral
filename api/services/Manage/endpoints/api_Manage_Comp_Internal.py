# This script implements the User Management CRUD actions: Create, Update, Delete
# from flask_login import login_required, current_user
from flask_restplus import Resource
from flask import request
# importando configuraciones desde modulo de inicio (__init__.py)
from . import api
from . import default_error_handler
from . import serializers as srl
from dto.mongo_engine_handler.Components.Comp_Root import *

# creating this endpoint
ns = api.namespace('component-internal', description='Administración de componentes internal')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/comp-root/<string:cmp_root_id>/comp-internal/<string:cmp_intr_id>')
class ComponentAPIByID(Resource):

    def get(self, cmp_root_id: str = "Public Id del componente root",
            cmp_intr_id: str = "Public Id del componente internal"):
        """ Obtener el componente internal mediante cmp_root_id e cmp_intr_id """
        try:
            componente_root = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if componente_root is None:
                return dict(success=False, msg="No existen componentes root asociados a este Public Id"), 404
            Success, result = componente_root.search_internal_by_id(cmp_intr_id)
            if not Success:
                return dict(success=False, msg="No existen componentes internal asociados a este Public Id"), 404
            return dict(success=True, componente=result.to_dict(), msg=f"{result} fue encontrado", ), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/comp-root/<string:cmp_root_id>')
class ComponentInternalInRootAPI(Resource):
    @api.expect(ser_from.internalcomponent)
    def post(self, cmp_root_id="Id del root"):
        """ Crea un nuevo componente internal dentro de un root """
        try:
            data = request.get_json()
            componente_internal = ComponenteInternal(**data)
            componenterootdb = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if componenterootdb is None:
                return dict(success=False, component_root=None,
                            msg=f'El componente root asociado a {cmp_root_id} no existe'), 409
            componenterootdb.add_internal_component([componente_internal])
            componenterootdb.save()
            return dict(success=True, component_root=componenterootdb.to_dict(),
                        msg="El componente internal fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/comp-root/<string:cmp_root_id>/comp-internal/<string:cmp_intr_id>')
class ComponentInternalInInternalAPI(Resource):
    @api.expect(ser_from.internalcomponent)
    def post(self, cmp_root_id="Id del root", cmp_intr_id="Id del internal"):
        """ Crea un nuevo componente internal dentro de un internal """
        try:
            data = request.get_json()
            componenteinternal = ComponenteInternal(**data)
            componenterootdb = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if componenterootdb is None:
                return dict(success=False, component_root=None,
                            msg=f'No existe el componente root asociado a {cmp_root_id}'), 404
            success, result = componenterootdb.search_internal_by_id(cmp_intr_id)
            if not success:
                return dict(success=False, component_root=None,
                            msg=f'No existe el componente internal asociado a {cmp_intr_id}'), 404
            result.add_internal_component([componenteinternal])
            componenterootdb.save()
            return dict(success=True, component_root=componenterootdb.to_dict(),
                        msg="El componente internal fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/comp-root/<string:cmp_root_id>/comp-internal/<string:cmp_intr_id>/position')
class ComponentAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, cmp_root_id="Id del componente root", cmp_intr_id="Id del componente internal"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            component_root_db = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if component_root_db is None:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente root asociado a la id {cmp_root_id}"), 404
            success, result = component_root_db.search_internal_by_id(cmp_intr_id)
            if not success:
                return dict(success=False, component_internal=None,
                            msg=f"No existe el componente internal asociado a la id {cmp_intr_id}"), 404
            result.update_position_x_y(pos_x, pos_y)
            component_root_db.save()
            return dict(success=True, component_internal=result.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)


# TODO: Delete this function if is not used beacuse it was created in api_Management_Comp_Leaf
"""
@ns.route('/comp-root/<string:cmp_root_id>/comp-internal/<string:cmp_intr_id>/comp-leaf')
class ComponentLeafInInternalAPI(Resource):
    @api.expect(ser_from.componentleaf)
    def post(self, cmp_root_id="Id del root", cmp_intr_id="Id del componente internal"):
        # Crea un nuevo componente leaf dentro de un internal 
        try:
            data = request.get_json()
            component_leaf = ComponenteLeaf(**data)
            component_root = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if component_root is None:
                return dict(success=False, component_root=None,
                            msg=f'El componente root asociado a {cmp_root_id} no existe'), 409
            success, component_internal = component_root.search_internal_by_id(cmp_intr_id)
            if not success:
                return dict(succes=False, component_root=None, msg=component_internal), 409
            success, message = component_internal.add_leaf_component([component_leaf])
            if success:
                component_root.save()
                return dict(success=True, component_root=component_root.to_dict(), msg=message), 200
            return dict(success=False, component_root=None, msg=message), 409
        except Exception as e:
            return default_error_handler(e)
            
"""
