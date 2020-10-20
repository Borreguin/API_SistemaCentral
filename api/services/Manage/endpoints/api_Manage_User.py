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
from dto.sqlite_engine_handler.Users import User
from dto.sqlite_engine_handler.Groups import Group

# creating this endpoint
ns = api.namespace('user', description='Relativas a la administración de usuarios')
ser_from = srl.Serializers(api)
api = ser_from.add_serializers()


@ns.route('/<string:public_id>')
class UserAPIByID(Resource):

    def get(self, public_id: str = "Public Id del usuario"):
        """ Obtener el usuario mediante su public_id """
        try:
            user = User.query.filter_by(public_id=public_id).first()
            if user is None:
                return dict(success=False, user=None, msg="No existe el usuario"), 404
            return dict(success=True, user=user.to_dict(), msg=f"{user} fue encontrado"), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.user)
    def put(self, public_id: str = "Public Id del usuario"):
        """ Edita un usuario de la Base de Datos usando su id público"""
        try:
            edited_user = request.get_json()
            print(request.url_rule.rule, request.method)
            groups = Group.query.filter(Group.users.any(public_id=public_id)).all()
            print(current_user.group)
            user = User.query.filter_by(public_id=public_id).first()
            if user is None:
                return dict(success=False, msg="No se ha encontrado el usuario"), 404
            success, msg = user.update(edited_user)
            return dict(success=success, msg=msg), 200 if success else 409

        except Exception as e:
            return default_error_handler(e)

    def delete(self, public_id: str = "Public Id del usuario"):
        """ Eliminar un usuario mediante su public_id """
        try:
            user = User.query.filter_by(public_id=public_id).first()
            if user is None:
                return dict(success=False, msg="El usuario no existe"), 404
            success, msg = user.delete()
            return dict(success=success, msg=msg), 200 if success else 409
        except Exception as e:
            return default_error_handler(e)


@ns.route('s')
class UsersAPI(Resource):

    def get(self):
        """ Obtiene todos los usuarios existentes  """
        try:
            users = User.query.all()
            to_send = list()
            for user in users:
                to_send.append(user.to_dict())
            if len(users) == 0:
                return dict(success=False, users=None, msg="No existen usuarios"), 404
            else:
                return dict(success=True, users=to_send, msg=f"[{len(users)}] usuarios")
        except Exception as e:
            return default_error_handler(e)


@ns.route('')
class UserAPI(Resource):
    @api.expect(ser_from.user)
    def post(self):
        """ Crea un nuevo usuario """
        try:
            data = request.get_json()
            user = User(**data)
            if not user.has_valid_mail():
                return dict(success=False, msg="Email invalido para este usuario"), 400
            success, msg = user.commit()
            return dict(success=success, msg=msg), 200 if success else 409
        except Exception as e:
            return default_error_handler(e)


@login_required
@ns.route('/login')
class LogIn(Resource):
    @staticmethod
    def get(self):
        """ Genera un token JWT para autenticación del usuario """
        try:
            auth = request.authorization
            if not auth or not auth.username or not auth.password:
                return make_response('No se puede verificar las credenciales', 401,
                                     {'WWW-Authenticate': 'Basic realm="Credenciales no ingresadas"'})
            user = User.query.filter_by(user_name=auth.username).first()
            if not user:
                return make_response('No se puede verificar las credenciales', 401,
                                     {'WWW-Authenticate': 'Basic realm="No se puede verificar el usuario."'})
            if user.check_password(auth.password):
                success, token, msg = user.encode_auth_token()
                log.info(msg)
                return dict(success=success, token=token, msg=msg), 200 if success else 401
            else:
                log.warning(f"{user.user_name} ha intentado iniciar sesión")

            return make_response('No se puede verificar las credenciales', 401,
                                 {'WWW-Authenticate': 'Basic realm="Credenciales incorrectas, inicie sesión"'})
        except Exception as e:
            return default_error_handler(e)
