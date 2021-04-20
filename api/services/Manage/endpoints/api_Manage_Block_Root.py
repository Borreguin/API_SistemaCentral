# This script implements the User Management CRUD actions: Create, Update, Delete
# from flask_login import login_required, current_user
from flask_restplus import Resource
from flask import request
# importando configuraciones desde modulo de inicio (__init__.py)
from . import api
from . import default_error_handler
from . import serializers as srl
from dto.mongo_engine_handler.Blocks.Block_Root import *

# creating this endpoint
ns = api.namespace('block-root', description='Administración de bloque root')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/<string:blk_root_id>')
class BlockAPI(Resource):
    @api.expect(ser_from.blockroot)
    def post(self, blk_root_id: str = "Public Id del bloque root"):
        """ Crea un nuevo bloque root """
        try:
            data = request.get_json()
            blockroot = BloqueRoot(public_id=blk_root_id, name=data['name'])
            blockrootdb = BloqueRoot.objects(public_id=blk_root_id).first()
            if not blockrootdb is None:
                return dict(success=False, bloqueroot=None, msg='Este bloque ya existe'), 409
            blockroot.save()
            return dict(success=True, bloqueroot=blockroot.to_dict(),
                        msg="El bloque root fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)

    def get(self, blk_root_id: str = "Public Id del bloque root"):
        """ Obtener el bloque root mediante su blk_root_id """
        try:
            block_root = BloqueRoot.objects(public_id=blk_root_id).first()
            if block_root is None:
                return dict(success=False, msg="No existen componentes root asociados a este Public Id"), 404
            return dict(success=True, bloqueroot=block_root.to_dict(), msg=f"{block_root} fue encontrado", ), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.blockroot)
    def put(self, blk_root_id: str = "Public Id del bloque root"):
        """ Edita un bloque root """
        try:
            data = request.get_json()
            blockrootdb = BloqueRoot.objects(public_id=blk_root_id).first()
            if blockrootdb is None:
                return dict(success=False, bloqueroot=None, msg='Este bloque no existe'), 409
            success, msg = blockrootdb.edit_root_block(data)
            if success:
                blockrootdb.save()
            return dict(success=success, bloqueroot=blockrootdb.to_dict(),
                        msg=msg)
        except Exception as e:
            return default_error_handler(e)


@ns.route('/<string:blk_root_id>/valid-operation')
class OperationAPI(Resource):
    @api.expect(ser_from.operation)
    def put(self, blk_root_id: str = "Public Id del bloque root"):
        """ Valida si una operación es correcta """
        try:
            data = request.get_json()
            blockrootdb = BloqueRoot.objects(public_id=blk_root_id).first()
            if blockrootdb is None:
                return dict(success=False, bloqueroot=None, msg='Este bloque no existe'), 409
            success, msg = blockrootdb.add_operations(data["topology"])
            if success:
                blockrootdb.save()
            return dict(success=success, bloqueroot=blockrootdb.to_dict(),
                        msg=msg)
        except Exception as e:
            return default_error_handler(e)


@ns.route('/<string:blk_root_id>/position')
class ComponentPositionAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, blk_root_id="Id del bloque root"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            block_root_db = BloqueRoot.objects(public_id=blk_root_id).first()
            if block_root_db is None:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente root asociado a la id {blk_root_id}"), 404
            block_root_db.update_position_x_y(pos_x, pos_y)
            block_root_db.save()
            return dict(success=True, bloqueroot=block_root_db.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/<string:blk_root_id>/operation')
class OperationAPI(Resource):
    @api.expect(ser_from.position)
    def put(self, blk_root_id="Id del bloque root"):
        """ Actualiza la posición x e y """
        try:
            data = request.get_json()
            pos_x = data["pos_x"]
            pos_y = data["pos_y"]
            block_root_db = BloqueRoot.objects(public_id=blk_root_id).first()
            if block_root_db is None:
                return dict(success=False, component_leaf=None,
                            msg=f"No existe el componente root asociado a la id {blk_root_id}"), 404
            block_root_db.update_position_x_y(pos_x, pos_y)
            block_root_db.save()
            return dict(success=True, bloqueroot=block_root_db.to_dict(), msg="Se actualizó position (x, y)")
        except Exception as e:
            return default_error_handler(e)
