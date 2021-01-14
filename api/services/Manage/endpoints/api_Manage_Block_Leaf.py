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


@ns.route('/block-root/<blk_root_id>/block-leaf/<blk_leaf_id>/position')
class BloqueAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, blk_root_id="Id del componente root", blk_leaf_id="Id del componente leaf"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            block_root_db = BloqueRoot.objects(public_id=blk_root_id).first()
            if block_root_db is None:
                return dict(success=False, bloque_leaf=None, msg=f"No existe el bloque root asociado a la id {blk_root_id}")
            success, result = block_root_db.search_leaf_by_id(blk_leaf_id)
            if not success:
                return dict(success=False, bloque_leaf=None, msg=f"No existe el bloque leaf asociado a la id {blk_leaf_id}")
            result.update_position_x_y(data["pos_x"], data["pos_y"])
            block_root_db.save()
            return dict(success=True, bloque_leaf=result.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/block-root/<string:blk_root_id>/block-leaf/<string:blk_leaf_id>')
class BlocLeafByID(Resource):

    def get(self, blk_root_id: str = "Public Id del bloque root",
            blk_leaf_id: str = "Public Id del bloque leaf"):
        """ Obtener el bloque leaf mediante su public_id y public_id del bloque root"""
        try:
            bloque_root = BloqueRoot.objects(public_id=blk_root_id).first()
            # bloque_root = BloqueRoot()
            if bloque_root is None:
                return dict(success=False, msg="No existen bloques root asociados a este Public Id"), 404
            success, result = bloque_root.search_leaf_by_id(blk_leaf_id)
            if not success:
                return dict(success=False, msg="No existen bloques leaf asociados a este Public Id"), 404
            return dict(success=True, bloqueleaf=result.to_dict(), msg=f"{result.name}​​ fue encontrado"), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.blockroot)
    def put(self, blk_root_id: str = "Public Id del bloque root",
            blk_leaf_id: str = "Public Id del bloque leaf"):
        """ Edita un bloque leaf de la Base de Datos usando su public_id y public_id del bloque root"""
        try:
            edited_block = request.get_json()
            bloque_root = BloqueRoot.objects(public_id=blk_root_id).first()
            if bloque_root is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existen bloques root asociados a este Public Id"), 404
            success, edited, msg = bloque_root.edit_leaf_by_id(blk_leaf_id, edited_block)
            if success:
                bloque_root.save()
                for comp in edited.comp_roots:
                    comp.save()
            return dict(success=success, bloqueroot=bloque_root.to_dict(), msg=msg), 200 if success else 409
        except Exception as e:
            return default_error_handler(e)

    def delete(self, blk_root_id: str = "Public Id del bloque root",
               blk_leaf_id: str = "Public Id del bloque leaf"):
        """ Eliminar bloque leaf mediante su public_id y public_id del bloque root"""
        try:
            bloque_root = BloqueRoot.objects(public_id=blk_root_id).first()
            if bloque_root is None:
                return dict(success=False, bloqueroot=None, msg="El bloque root no existe"), 404
            success_1, leaf_block = bloque_root.search_leaf_by_id(blk_leaf_id)
            success_2, msg = bloque_root.delete_leaf_by_id(blk_leaf_id)
            if success_1 and success_2:
                for comp in leaf_block.comp_roots:
                    comp.delete()
                bloque_root.save()
                return dict(success=True, bloqueroot=bloque_root.to_dict(), msg=msg), 200
            return dict(success=False, bloqueroot=bloque_root.to_dict(), msg=msg)
        except Exception as e:
            return default_error_handler(e)


@ns.route('/block-root/<string:blk_root_id>')
class Block_leafAPI(Resource):
    @api.expect(ser_from.blockroot)
    def post(self, blk_root_id: str = "Public Id del bloque root"):
        """ Crea un nuevo bloque leaf usando blk_root_id del bloque root """
        try:
            data = request.get_json()
            bloqueleaf = BloqueLeaf(**data)
            bloqueroot_db = BloqueRoot.objects(public_id=blk_root_id).first()
            if bloqueroot_db is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existen bloques root asociados a este Public Id"), 404
            success, msg = bloqueroot_db.add_new_leaf_block([bloqueleaf])
            if success:
                bloqueroot_db.save()
            return dict(success=success, bloqueroot=bloqueroot_db.to_dict(), msg=msg)
        except Exception as e:
            return default_error_handler(e)


@ns.route('/<string:blk_leaf_id>')
class BlockLeafByIDAPI(Resource):
    def get(self, blk_leaf_id: str = "Public Id del bloque leaf"):
        """ Obtiene el bloque leaf usando su blk_root_id  """
        try:
            bloqueroot_db = BloqueRoot.objects(block_leafs__match={"public_id": blk_leaf_id}).first()
            if bloqueroot_db is None:
                return dict(success=False, bloqueroot=None,
                            msg="No existen bloques root asociados a este Public Id"), 404
            bloqueroot_db.search_leaf_by_id(blk_leaf_id)
            return dict(success=True, bloqueroot=bloqueroot_db.to_dict(), msg="test")
        except Exception as e:
            return default_error_handler(e)
