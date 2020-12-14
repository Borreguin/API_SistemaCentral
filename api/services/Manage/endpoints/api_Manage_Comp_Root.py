# This script implements the User Management CRUD actions: Create, Update, Delete
#from flask_login import login_required, current_user
from flask_restplus import Resource
from flask import request,  make_response
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

    @api.expect(ser_from.rootcomponent)
    def put(self, public_id: str = "Public Id del componente root"):
        """ Edita un componente root de la Base de Datos usando su public_id"""
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
    #TODO: CAMBIAR PARA NO DEJARSE ELIMINAR LIBREMENTE
    #ELIMINACIÓN A NIVEL DE BLOQUE LEAF
    def delete(self, public_id: str = "Public Id del componente"):
        """ Eliminar un componente root mediante su public_id """
        try:
            componenteroot=ComponenteRoot.objects(public_id=public_id).first()
            if componenteroot is None:
                return dict(success=False, msg="El componente root no existe"),404
            #eliminando componente root por Public id
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


@ns.route('/<string:root_block_id>/<string:leaf_block_id>')
class CompRootAPI(Resource):
    @api.expect(ser_from.rootcomponentname)
    def post(self, root_block_id, leaf_block_id):
        """ Crea un nuevo componente root """
        try:
            # Buscando Bloque root y Bloque Leaf asociado
            root_block_db = BloqueRoot.objects(public_id=root_block_id).first()
            if root_block_db is None:
                return dict(success=False, rootcomponent=None, msg="No existe un bloque asociado a este id"), 404
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
            return dict(success=True, rootcomponent=root_component.to_dict(), msg=msg), 200
        except Exception as e:
            return default_error_handler(e)
