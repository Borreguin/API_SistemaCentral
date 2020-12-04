# This script implements the User Management CRUD actions: Create, Update, Delete
from flask_login import login_required, current_user
from flask_restplus import Resource
from flask import request,  make_response
# importando configuraciones desde modulo de inicio (__init__.py)
from dto.mongo_engine_handler.Block_Root import BloqueRoot, BloqueLeaf
from . import api
from . import default_error_handler
from . import serializers as srl
from . import parsers
from . import log
from dto.mongo_engine_handler.Comp_Internal import *
from dto.mongo_engine_handler.Comp_Leaf import *
from dto.mongo_engine_handler.Comp_Root import *

# creating this endpoint
ns = api.namespace('block-leaf', description='Administración de bloque Leaf')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/position/<id_root>/<id_leaf>')
class ComponentAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, id_root="Id del componente root", id_leaf="Id del componente leaf"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            block_root_db = BloqueRoot.objects(public_id=id_root).first()
            if block_root_db is None:
                return dict(success=False, bloque_leaf=None, msg=f"No existe el bloque root asociado a la id {id_root}")
            success, result = block_root_db.search_leaf_by_id(id_leaf)
            if not success:
                return dict(success=False, bloque_leaf=None, msg=f"No existe el bloque leaf asociado a la id {id_leaf}")
            result.update_position_x_y(data["pos_x"], data["pos_y"])
            block_root_db.save()
            return dict(success=True, bloque_leaf=result.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/<string:block_public_id>/leaf/<string:leaf_public_id>')
class BlocLeafByID(Resource):

    def get(self, block_public_id: str = "Public Id del bloque root",
            leaf_public_id: str = "Public Id del bloque leaf"):
        """ Obtener el bloque leaf mediante su public_id y public_id del bloque root"""
        try:
            bloque_root = BloqueRoot.objects(public_id=block_public_id).first()
            # bloque_root = BloqueRoot()
            if bloque_root is None:
                return dict(success=False, msg="No existen bloques root asociados a este Public Id"), 404
            success, result = bloque_root.search_leaf_by_id(leaf_public_id)
            if not success:
                return dict(success=False, msg="No existen bloques leaf asociados a este Public Id"), 404
            return dict(success=True, bloqueleaf=result.to_dict(), msg=f"{result.name}​​ fue encontrado"), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.blockroot)
    def put(self, block_public_id: str = "Public Id del bloque root",
            leaf_public_id: str = "Public Id del bloque leaf"):
        """ Edita un bloque leaf de la Base de Datos usando su public_id y public_id del bloque root"""
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
            success, mensaje = bloque_root.delete_leaf_by_id(leaf_public_id)
            if success:
                bloque_root.save()
                return dict(success=True, msg=mensaje), 200
            return dict(success=False, msg=mensaje)
        except Exception as e:
            return default_error_handler(e)


#####################################################
@ns.route('/<string:block_public_id>/leaf')
class Block_leafAPI(Resource):
    @api.expect(ser_from.blockroot)
    def post(self, block_public_id: str = "Public Id del bloque root"):
        """ Crea un nuevo bloque leaf usando public_id del bloque root """
        try:
            data = request.get_json()
            bloqueleaf = BloqueLeaf(name=data['name'])
            bloqueroot_db = BloqueRoot.objects(public_id=block_public_id).first()
            if bloqueroot_db is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existen bloques root asociados a este Public Id"), 404
            success, mensaje = bloqueroot_db.add_leaf_block([bloqueleaf])
            if success:
                bloqueroot_db.save()
                return dict(success=True, msg=f"El bloque leaf {data['name']} fue ingresado en la base de datos")
            return dict(success=False, msg="El bloque leaf no fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)