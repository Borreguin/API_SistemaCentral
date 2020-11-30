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

    @api.expect(ser_from.rootcomponent)
    def put(self, public_id: str = "Public Id del componente root"):
        """ Edita un componente root de la Base de Datos usando su id público"""
        try:
            edited_component = request.get_json()
            componenteroot=ComponenteRoot.objects(public_id=public_id).first()
            if componenteroot is None:
                return dict(success=False, msg="No existen componentes root asociados a este Public Id"), 404
            componenteroot.block=edited_component["block"]
            componenteroot.name=edited_component["name"]
            componenteroot.save()
            return dict(success=True, componenteroot=componenteroot.to_dict(),
                        msg=f"El componente root {componenteroot} fue editado"), 200
        except Exception as e:
            return default_error_handler(e)

    def delete(self, public_id: str = "Public Id del componente"):
        """ Eliminar un componente root mediante su public_id """
        try:
            componenteroot = ComponenteRoot.objects(public_id=public_id).first()
            if componenteroot is None:
                return dict(success=False, msg="El componente root no existe"), 404
            # eliminando componente root por Public id
            componenteroot.delete()
            return dict(success=True,
                        msg=f"El componente root {componenteroot} fue eliminado"), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('s')
class ComponentAPI(Resource):

    def get(self):
        """ Obtiene todos los componentes root existentes  """
        try:
            componentesroot = ComponenteRoot.objects()
            to_send = list()
            for componenteroot in componentesroot:
                to_send.append(componenteroot.to_dict())
            if len(componentesroot) == 0:
                return dict(success=False, componentesroot=None, msg="No existen componentes root"), 404
            else:
                return dict(success=True, componentesroot=to_send, msg=f"[{len(componentesroot)}] componentes root")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/')
class ComponentAPI(Resource):
    @api.expect(ser_from.rootcomponent)
    def post(self):
        """ Crea un nuevo componente root """
        try:
            data = request.get_json()
            componenteroot = ComponenteRoot(**data)
            componenterootdb = ComponenteRoot.objects(block=data['block'], name=data['name']).first()
            if not componenterootdb is None:
                return dict(success=False, msg='Este componente root ya existe'), 409
            componenteroot.save()
            return dict(success=True, msg="El componente root fue ingresado en la base de datos")
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


####################################################

@ns.route('/<string:block_public_id>/leaf/<string:leaf_public_id>')
class ComponentAPIByID(Resource):

    def get(self, block_public_id: str = "Public Id del bloque root",
            leaf_public_id: str = "Public Id del bloque leaf"):
        """ Obtener el bloque leaf mediante su public_id y public_id del bloque root"""
        try:
            bloque_root = BloqueRoot.objects(public_id=block_public_id).first()
            # bloque_root = BloqueRoot()
            if bloque_root is None:
                return dict(success=False, msg="No existen bloques root asociados a este Public Id"), 404
            Success, result = bloque_root.search_leaf_by_id(leaf_public_id)
            if not Success:
                return dict(success=False, msg="No existen bloques leaf asociados a este Public Id"), 404
            return dict(success=True, bloqueleaf=result.to_dict(), msg=f"{result.name} fue encontrado"), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.blockroot)
    def put(self, block_public_id: str = "Public Id del bloque root",
            leaf_public_id: str = "Public Id del bloque leaf"):
        """ Edita un bloque leaf de la Base de Datos usando su id público y block_public_id"""
        try:
            edited_block = request.get_json()
            bloque_root = BloqueRoot.objects(public_id=block_public_id).first()
            if bloque_root is None:
                return dict(success=False, block=None, msg="No existen bloques root asociados a este Public Id"), 404
            success, edited, mensaje = bloque_root.edit_leaf_by_id(leaf_public_id, edited_block)
            if not success:
                return dict(success=False, block=None, msg=mensaje), 409
            bloque_root.save()
            return dict(success=True, block=edited.to_dict(), msg=mensaje), 200
        except Exception as e:
            return default_error_handler(e)

    def delete(self, block_public_id: str = "Public Id del bloque root",
               leaf_public_id: str = "Public Id del bloque leaf"):
        """ Eliminar bloque leaf mediante su public_id y public_id del bloque root"""
        try:
            bloque_root = BloqueRoot.objects(public_id=block_public_id).first()
            if bloque_root is None:
                return dict(success=False, msg="El bloque root no existe"), 404
            success, mensaje = bloque_root.delete_leaf_by_id(
                leaf_public_id)  # si bloque leaf no existe igual sale como que lo eliminó
            if success:
                bloque_root.save()
                return dict(success=True, msg=f'{mensaje}'), 200
            return dict(success=False, msg=f'{mensaje}')
        except Exception as e:
            return default_error_handler(e)
