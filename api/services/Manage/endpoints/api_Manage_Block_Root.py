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


@ns.route('/<string:block_public_id>')
class BlockAPI(Resource):
    @api.expect(ser_from.blockroot)
    def post(self, block_public_id: str = "Public Id del bloque root"):
        """ Crea un nuevo bloque root """
        try:
            data = request.get_json()
            blockroot = BloqueRoot(public_id=block_public_id, name=data['name'])
            blockrootdb = BloqueRoot.objects(public_id=block_public_id).first()
            if not blockrootdb is None:
                return dict(success=False, bloque_root=None, msg='Este bloque root ya existe'), 409
            blockroot.save()
            return dict(success=True, bloque_root=blockroot.to_dict(),
                        msg="El bloque root fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)

    def delete(self, public_id: str = "Public Id del componente"):
        """ Eliminar un bloque root mediante su public_id """
        try:
            bloqueroot = BloqueRoot.objects(public_id=public_id).first()
            if bloqueroot is None:
                return dict(success=False, msg="El componente root no existe"), 404
            # eliminando componente root por Public id
            bloqueroot.delete()
            return dict(success=True,
                        msg=f"El componente root {bloqueroot} fue eliminado"), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/<string:public_id>')
class BlockAPIByID(Resource):

    def get(self, public_id: str = "Public Id del bloque root"):
        """ Obtener el bloque root mediante su public_id """
        try:
            block_root = ComponenteRoot.objects(public_id=public_id).first()
            if block_root is None:
                return dict(success=False, msg="No existen componentes root asociados a este Public Id"), 404
            return dict(success=True, bloqueroot=block_root.to_dict(), msg=f"{block_root} fue encontrado", ), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.rootcomponent)
    def put(self, public_id: str = "Public Id del componente root"):
        """ Edita un componente root de la Base de Datos usando su id público"""
        try:
            edited_component = request.get_json()
            componenteroot = ComponenteRoot.objects(public_id=public_id).first()
            if componenteroot is None:
                return dict(success=False, msg="No existen componentes root asociados a este Public Id"), 404
            componenteroot.block = edited_component["block"]
            componenteroot.name = edited_component["name"]
            componenteroot.save()
            return dict(success=True, bloqueroot=componenteroot.to_dict(),
                        msg=f"El componente root {componenteroot} fue editado"), 200
        except Exception as e:
            return default_error_handler(e)
