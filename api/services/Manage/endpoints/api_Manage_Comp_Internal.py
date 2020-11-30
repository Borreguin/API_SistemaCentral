# This script implements the User Management CRUD actions: Create, Update, Delete
from flask_login import login_required, current_user
from flask_restplus import Resource
from flask import request,  make_response
# importando configuraciones desde modulo de inicio (__init__.py)
from . import api
from . import default_error_handler
from . import serializers as srl
from . import parsers
from . import log
from dto.mongo_engine_handler.Comp_Internal import *
from dto.mongo_engine_handler.Comp_Leaf import *
from dto.mongo_engine_handler.Comp_Root import *


# creating this endpoint
ns = api.namespace('component-internal', description='Administración de componentes internal')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/root/<string:root_public_id>/internal/<string:internal_public_id>')
class ComponentAPIByID(Resource):

    def get(self, root_public_id: str = "Public Id del componente root",
            internal_public_id: str = "Public Id del componente internal"):
        """ Obtener el componente internal mediante root_public_id e internal_public_id """
        try:
            componente_root = ComponenteRoot.objects(public_id=root_public_id).first()
            if componente_root is None:
                return dict(success=False, msg="No existen componentes root asociados a este Public Id"), 404
            Success,result = componente_root.search_internal_by_id(internal_public_id)
            if not Success:
                return dict(success=False, msg="No existen componentes internal asociados a este Public Id"), 404
            return dict(success=True, componente=result.to_dict(),msg=f"{result} fue encontrado", ), 200
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
            componenteroot=ComponenteRoot.objects(public_id=public_id).first()
            if componenteroot is None:
                return dict(success=False, msg="El componente root no existe"),404
            #eliminando componente root por Public id
            componenteroot.delete()
            return dict(success=True,
                        msg=f"El componente root {componenteroot} fue eliminado"), 200
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


@ns.route('/<id_root>')
class ComponentInternalInRootAPI(Resource):
    @api.expect(ser_from.internalcomponent)
    def post(self, id_root="Id del root"):
        """ Crea un nuevo componente internal dentro de un root """
        try:
            data = request.get_json()
            componente_internal = ComponenteInternal(**data)
            componenterootdb = ComponenteRoot.objects(public_id=id_root).first()
            if componenterootdb is None:
                return dict(success=False, component_root=None,
                            msg=f'El componente root asociado a {id_root} no existe'), 409
            componenterootdb.add_internal_component([componente_internal])
            componenterootdb.save()
            return dict(success=True, component_root=componenterootdb.to_dict(),
                        msg="El componente internal fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/<id_root>/<id_internal>')
class ComponentInternalInInternalAPI(Resource):
    @api.expect(ser_from.internalcomponent)
    def post(self, id_root="Id del root", id_internal="Id del internal"):
        """ Crea un nuevo componente internal dentro de un internal """
        try:
            data = request.get_json()
            componenteinternal = ComponenteInternal(**data)
            componenterootdb = ComponenteRoot.objects(public_id=id_root).first()
            if componenterootdb is None:
                return dict(success=False, component_root=None,
                            msg=f'No existe el componente root asociado a {id_root}'), 404
            success, result = componenterootdb.search_internal_by_id(id_internal)
            if not success:
                return dict(success=False, component_root=None,
                            msg=f'No existe el componente internal asociado a {id_internal}'), 404
            result.add_internal_component([componenteinternal])
            componenterootdb.save()
            return dict(success=True, component_root=componenterootdb.to_dict(),
                        msg="El componente root fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)