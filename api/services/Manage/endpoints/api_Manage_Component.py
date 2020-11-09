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
from dto.mongo_engine_handler.Components import *


# creating this endpoint
ns = api.namespace('component', description='Administración de componentes')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/root/<string:public_id>')
class ComponentAPIByID(Resource):

    def get(self, public_id: str = "Public Id del componente root"):
        """ Obtener el componente root mediante su public_id """
        try:
            # componenteroot=ComponenteRoot.search_internal_by_id(id_internal=public_id).first() #no hay función en components que permita obtener root por id
            # if componenteroot is None:
            #     return dict(success=False, componenteroot=None, msg="No existe el componente root"),404
            # return dict(success=True, componenteroot=componenteroot.to_dict(), msg=f"{componenteroot} fue encontrado"),200
            #user = User.query.filter_by(public_id=public_id).first()
            #if user is None:
              #  return dict(success=False, user=None, msg="No existe el usuario"), 404
            #return dict(success=True, user=user.to_dict(), msg=f"{user} fue encontrado"), 200
            return dict(success=False, msg="Función no implementada todavía")
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.rootcomponent)
    def put(self, public_id: str = "Public Id del componente root"):
        """ Edita un componente root de la Base de Datos usando su id público"""
        try:
            edited_component = request.get_json()
            #user = User.query.filter_by(public_id=public_id).first()
            #if user is None:
                #return dict(success=False, msg="No se ha encontrado el usuario"), 404
            #success, msg = user.update(edited_user)
            #return dict(success=success, msg=msg), 200 if success else 409
            return dict(success=False, msg="Función no implementada todavía")
        except Exception as e:
            return default_error_handler(e)

    def delete(self, public_id: str = "Public Id del componente"):
        """ Eliminar un componete root mediante su public_id """
        try:
            #user = User.query.filter_by(public_id=public_id).first()
            #if user is None:
                #return dict(success=False, msg="El usuario no existe"), 404
            #success, msg = user.delete()
            #return dict(success=success, msg=msg), 200 if success else 409
            return dict(success=False, msg="Función no implementada todavía")
        except Exception as e:
            return default_error_handler(e)


@ns.route('s/root')
class ComponentAPI(Resource):

    def get(self):
        """ Obtiene todos los componentes root existentes  """
        try:
            # users = User.query.all()
            # to_send = list()
            # for user in users:
            #     to_send.append(user.to_dict())
            # if len(users) == 0:
            #     return dict(success=False, users=None, msg="No existen usuarios"), 404
            # else:
            #     return dict(success=True, users=to_send, msg=f"[{len(users)}] usuarios")
            return dict(success=False, msg="Función no implementada todavía")
        except Exception as e:
            return default_error_handler(e)


@ns.route('/root')
class ComponentAPI(Resource):
    @api.expect(ser_from.rootcomponent)
    def post(self):
        """ Crea un nuevo componente root """
        try:
            data = request.get_json()
            componenteroot = ComponenteRoot(**data)
            componenterootdb=ComponenteRoot.objects(bloque=data['bloque'], nombre=data['nombre']).first()
            if not componenterootdb is None:
                return dict(success=False,msg='Este componente root ya existe'),409
            componenteroot.save()
            return dict(success=True, msg="El componente root fue ingresado en la base de datos")
        except Exception as e:
            return default_error_handler(e)