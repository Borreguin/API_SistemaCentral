# This script implements the User Management CRUD actions: Create, Update, Delete
#from flask_login import login_required, current_user
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
ns = api.namespace('component-root', description='Administración de componentes Root')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/<string:public_id>')
class ComponentAPIByID(Resource):

    def get(self, public_id: str = "Public Id del componente root"):
        """ Obtener el componente root mediante su public_id """
        try:
            componente  = ComponenteRoot.objects(public_id=public_id).first()
            if componente is None:
                return dict(success=False, msg="No existen componentes root asociados a este Public Id"), 404
            return dict(success=True, componente=componente.to_dict(),msg=f"{componente} fue encontrado", ), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('s')
class ComponentAPI(Resource):

    def get(self):
        """ Obtiene todos los componentes root existentes  """
        try:
            componentesroot=ComponenteRoot.objects()
            to_send=list()
            for componenteroot in componentesroot:
                to_send.append(componenteroot.to_dict())
            if len(componentesroot) == 0:
                return dict(success=False, componentesroot=None, msg="No existen componentes root"), 404
            else:
                return dict(success=True, componentesroot=to_send,msg=f"[{len(componentesroot)}] componentes root")
        except Exception as e:
            return default_error_handler(e)



@ns.route('/<string:root_block_id>/block-leaf/<string:leaf_block_id>')
class CompRootAPI(Resource):
    @api.expect(ser_from.rootcomponentname)
    def post(self, root_block_id, leaf_block_id):
        """ Crea un nuevo componente root """
        try:
            # Buscando Bloque root y Bloque Leaf asociado
            root_block_db = BloqueRoot.objects(public_id=root_block_id).first()
            if root_block_db is None:
                return dict(success=False, rootcomponent=None,
                            msg="No existe un bloque general asociado a este id"), 404
            success, leaf_block_db = root_block_db.search_leaf_by_id(leaf_block_id)
            if not success:
                return dict(success=False, rootcomponent=None,
                            msg="No existe un bloque interno asociado a este id"), 404
            # Creando el componente nuevo
            data = request.get_json()
            root_component = ComponenteRoot(block=leaf_block_db.name, **data)
            success, msg = leaf_block_db.add_new_root_component([root_component])
            if success:
                root_component.save()
                root_block_db.save()
                return dict(success=success, bloqueroot=root_block_db.to_dict(), msg=msg), 200
            return dict(success=success, root_component=None, msg=msg), 404
        except Exception as e:
            return default_error_handler(e)


# EndPoints que utilizan la estructura general
@ns.route('/<string:root_component_id>/block-root/<string:root_block_id>/block-leaf/<string:leaf_block_id>')
class CompRootAPI(Resource):

    def delete(self, root_block_id: str, leaf_block_id: str, root_component_id: str):
        """ Elimina un componente root mediante: id del bloque root, id del bloque leaf e id del componente """
        try:
            # Buscando Bloque root y Bloque Leaf asociado
            root_block_db = BloqueRoot.objects(public_id=root_block_id).first()
            if root_block_db is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existe un bloque general asociado a este id"), 404
            root_component_db = ComponenteRoot.objects(public_id=root_component_id).first()
            if root_component_db is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existe el componente asociado a este id"), 404
            success, leaf_block_db = root_block_db.search_leaf_by_id(leaf_block_id)
            if not success:
                return dict(success=False, bloqueroot=None,
                            msg="No existe un bloque interno asociado a este id"), 404

            success, msg = leaf_block_db.delete_root_component_by_id(root_component_id)
            if success:
                root_component_db.delete()
                root_block_db.save()
            return dict(success=success, bloqueroot=root_block_db.to_dict(),
                        msg=msg), 200 if success else 409

        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.rootcomponentname)
    def put(self, root_block_id: str, leaf_block_id: str, root_component_id: str):
        """ Edita un componente root mediante: id del bloque root, id del bloque leaf e id del componente"""
        try:
            # Buscando Bloque root y Bloque Leaf asociado
            root_block_db = BloqueRoot.objects(public_id=root_block_id).first()
            if root_block_db is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existe un bloque general asociado a este id"), 404

            # Buscando el Bloque leaf asociado
            success, leaf_block_db = root_block_db.search_leaf_by_id(leaf_block_id)
            if not success:
                return dict(success=False, bloqueroot=None,
                            msg="No existe un bloque interno asociado a este id"), 404
            # Editando el componente root:
            edited_component = request.get_json()
            edited_component["block"] = leaf_block_db.name
            root_component_db = ComponenteRoot.objects(public_id=root_component_id).first()
            if root_component_db is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existe componente root asociados a este public id"), 404
            same_name = [True for comp in leaf_block_db.comp_roots if comp.name == edited_component["name"]]
            if any(same_name):
                return dict(success=False, bloqueroot=None, msg="Ya existe un componente con este nombre"), 409
            success, msg = root_component_db.edit_root_component(edited_component)
            if success:
                root_component_db.save()
                root_block_db = BloqueRoot.objects(public_id=root_block_id).first()
            return dict(success=success, bloqueroot=root_block_db.to_dict(),
                        msg=msg), 200 if success else 409
        except Exception as e:
            return default_error_handler(e)
          

@ns.route('/position/<id_root>')
class ComponentPositionAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, id_root="Id del componente root"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            component_root_db = ComponenteRoot.objects(public_id=id_root).first()
            if component_root_db is None:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente root asociado a la id {id_root}")
            component_root_db.update_position_x_y(pos_x, pos_y)
            component_root_db.save()
            return dict(success=True, component_root=component_root_db.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)
