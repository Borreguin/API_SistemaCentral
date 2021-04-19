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
ns = api.namespace('component-leaf', description='Administración de componentes Leaf')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/comp-root/<string:cmp_root_id>/comp-leaf/<string:cmp_leaf_id>')
class CompLeafByID(Resource):

    @api.expect(ser_from.componentleaf)
    def put(self, cmp_root_id: str = "Public Id del componente root",
            cmp_leaf_id: str = "Public Id del componente leaf"):
        """ Edita un componente leaf de la Base de Datos usando su public_id y public_id del componente root"""
        try:
            edited_component = request.get_json()
            component_root = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if component_root is None:
                return dict(success=False, component_root=None,
                            msg="No existen componentes root asociados a este Public Id"), 404
            success, component_leaf = component_root.search_leaf_by_id(cmp_leaf_id)
            if not success:
                return dict(success=False, component_root=None, msg=component_leaf), 409
            success, message = component_leaf.edit_leaf_component(edited_component)
            if success:
                component_root.save()
                return dict(success=True, component_root=component_root.to_dict(), msg=message), 200
            return dict(success=False, component_root=None, msg=message), 409
        except Exception as e:
            return default_error_handler(e)


@ns.route('/comp-root/<string:cmp_root_id>/comp-leaf/<string:cmp_leaf_id>/position')
class ComponentAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, cmp_root_id="Id del componente root", cmp_leaf_id="Id del componente leaf"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            component_root_db = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if component_root_db is None:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente root asociado a la id {cmp_root_id}")
            success, result = component_root_db.search_leaf_by_id(cmp_leaf_id)
            if not success:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente leaf asociado a la id {cmp_leaf_id}")
            result.update_position_x_y(pos_x, pos_y)
            component_root_db.save()
            return dict(success=True, component_leaf=result.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/comp-root/<string:cmp_root_id>/comp-internal/<string:cmp_intr_id>')
class ComponentAPI(Resource):
    @api.expect(ser_from.componentleaf)
    def post(self, cmp_root_id="Id del componente root", cmp_intr_id="Id del componente interno"):
        """ Crea un componente leaf dentro de un componente interno """
        try:
            data = request.get_json()
            component_root_db = ComponenteRoot.objects(public_id=cmp_root_id).first()
            if component_root_db is None:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente root asociado a la id {cmp_root_id}"), 404

            success, component_internal = component_root_db.search_internal_by_id(cmp_intr_id)
            if not success:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente interno asociado a la id {cmp_intr_id}"), 404

            pos_x, pos_y = data.pop("pos_x", None), data.pop("pos_x", None)
            new_leaf_component = ComponenteLeaf(**data)
            new_leaf_component.create_consignments_container()
            if pos_x is not None and pos_y is not None:
                new_leaf_component.update_position_x_y(pos_x, pos_y)
            success, msg = component_internal.add_leaf_component([new_leaf_component])
            if success:
                component_root_db.save()
            return dict(success=success,
                        component_leaf=new_leaf_component.to_dict() if success else None,
                        msg=msg), 200 if success else 409

        except Exception as e:
            return default_error_handler(e)
