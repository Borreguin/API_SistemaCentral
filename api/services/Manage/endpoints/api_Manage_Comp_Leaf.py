# This script implements the User Management CRUD actions: Create, Update, Delete
from flask_login import login_required, current_user
from flask_restplus import Resource
from flask import request,  make_response
# importando configuraciones desde modulo de inicio (__init__.py)
from dto.mongo_engine_handler.Block_Leaf import BloqueLeaf
from dto.mongo_engine_handler.Block_Root import BloqueRoot
from . import api
from . import default_error_handler
from . import serializers as srl
from . import parsers
from . import log
from dto.mongo_engine_handler.Comp_Internal import *
from dto.mongo_engine_handler.Comp_Leaf import *
from dto.mongo_engine_handler.Comp_Root import *


# creating this endpoint
ns = api.namespace('component-leaf', description='Administración de componentes Leaf')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/<string:root_public_id>/leaf/<string:leaf_public_id>')
class CompLeafByID(Resource):

    @api.expect(ser_from.componentleaf)
    def put(self, root_public_id: str = "Public Id del componente root",
            leaf_public_id: str = "Public Id del componente leaf"):
        """ Edita un componente leaf de la Base de Datos usando su public_id y public_id del componente root"""
        try:
            edited_component = request.get_json()
            component_root = ComponenteRoot.objects(public_id=root_public_id).first()
            if component_root is None:
                return dict(success=False, component_root=None, msg="No existen componentes root asociados a este Public Id"), 404
            success, component_leaf=component_root.search_leaf_by_id(leaf_public_id)
            if not success:
                return dict(success=False, component_root=None, msg=component_leaf), 409
            success, message=component_leaf.edit_leaf_component(edited_component)
            if success:
                component_root.save()
                return dict(success=True, component_root=component_root.to_dict(), msg=message), 200
            return dict(success=False, component_root=None, msg=message), 409
        except Exception as e:
            return default_error_handler(e)

@ns.route('/position/<id_root>/<id_leaf>')
class ComponentAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, id_root="Id del componente root", id_leaf="Id del componente leaf"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            component_root_db = ComponenteRoot.objects(public_id=id_root).first()
            if component_root_db is None:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente root asociado a la id {id_root}")
            success, result = component_root_db.search_leaf_by_id(id_leaf)
            if not success:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente leaf asociado a la id {id_leaf}")
            result.update_position_x_y(pos_x, pos_y)
            component_root_db.save()
            return dict(success=True, component_leaf=result.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)

