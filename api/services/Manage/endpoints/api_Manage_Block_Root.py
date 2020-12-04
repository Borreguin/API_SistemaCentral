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







