# This script implements the User Management CRUD actions: Create, Update, Delete
from flask_login import login_required, current_user
from flask_restplus import Resource
from flask import request, make_response
# importando configuraciones desde modulo de inicio (__init__.py)
from dto.mongo_engine_handler.Block_Root import BloqueRoot
from . import api
from . import default_error_handler
from . import serializers as srl
from . import parsers
from . import log
from dto.mongo_engine_handler.Comp_Internal import *
from dto.mongo_engine_handler.Comp_Leaf import *
from dto.mongo_engine_handler.Comp_Root import *
from dto.mongo_engine_handler.Block_Root import *
from dto.mongo_engine_handler.Block_Leaf import *

# creating this endpoint
ns = api.namespace('block-root', description='Administración de bloque root')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/block/<string:block_public_id>/leaf/<string:leaf_public_id>')
class ComponentAPIByID(Resource):

    def get(self, block_public_id: str = "Public Id del bloque root",
            leaf_public_id: str="Public Id del bloque leaf"):
        """ Obtener el bloque leaf mediante su public_id y public_id del bloque root"""
        try:
            bloque_root = BloqueRoot.objects(public_id=block_public_id).first()
            #bloque_root = BloqueRoot()
            if bloque_root is None:
                return dict(success=False, msg="No existen bloques root asociados a este Public Id"), 404
            Success,result = bloque_root.search_leaf_by_id(leaf_public_id)
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
            success, edited, mensaje = bloque_root.edit_leaf_by_id(leaf_public_id,edited_block)
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
            success, mensaje = bloque_root.delete_leaf_by_id(leaf_public_id) #si bloque leaf no existe igual sale como que lo eliminó
            if success:
                bloque_root.save()
                return dict(success=True,msg=f'{mensaje}'), 200
            return dict(success=False, msg=f'{mensaje}')
        except Exception as e:
            return default_error_handler(e)


@ns.route('s/root')
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


@ns.route('/block/<string:block_public_id>')
class ComponentAPI(Resource):
    @api.expect(ser_from.blockroot)
    def post(self, block_public_id: str = "Public Id del bloque root"):
        """ Crea un nuevo bloque root """
        try:
            data = request.get_json()
            blockroot = BloqueRoot(public_id=block_public_id, name=data['name'])
            blockrootdb = BloqueRoot.objects(public_id=block_public_id, name=data['name']).first()
            if not blockrootdb is None:
                return dict(success=False, msg='Este bloque root ya existe'), 409
            blockroot.save()
            return dict(success=True, msg="El bloque root fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)

@ns.route('/block/<string:block_public_id>/leaf')
class Block_leafAPI(Resource):
    @api.expect(ser_from.blockroot)
    def post(self, block_public_id: str = "Public Id del bloque root"):
        """ Crea un nuevo bloque leaf usando public_id del bloque root """
        try:
            data = request.get_json()
            bloqueleaf = BloqueLeaf(name=data['name'])
            bloqueroot_db = BloqueRoot.objects(public_id=block_public_id).first()
            if bloqueroot_db is None:
                return dict(success=False, bloqueroot=None ,msg="No existen bloques root asociados a este Public Id"), 404
            success, mensaje = bloqueroot_db.add_leaf_block([bloqueleaf])
            if success:
                bloqueroot_db.save()
                return dict(success=True, msg=f"El bloque leaf {data['name']} fue ingresado en la base de datos")
            return dict(success=False, msg="El bloque leaf no fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)
