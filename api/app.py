""""
    Created by Roberto Sánchez A.
    API Sistema Central


"""
from api import *
from waitress import serve

# import the general configuration of this API:
# Custom import
from api.services.restplus_config import api as api_p
from settings import initial_settings as init
from api import app
#from api.authentication.auth import add_authentication

""" EndPoints """
# namespaces: Todos los servicios de esta API
from api.services.Manage.endpoints.api_Manage_Comp_Root import ns as namespace_Comp_Root
from api.services.Manage.endpoints.api_Manage_Comp_Internal import ns as namespace_Comp_Internal
from api.services.Manage.endpoints.api_Manage_Comp_Leaf import ns as namespace_Comp_Leaf
from api.services.Manage.endpoints.api_Manage_Block_Leaf import ns as namespace_Block_Leaf
from api.services.Manage.endpoints.api_Manage_Block_Root import ns as namespace_Block_Root
from api.services.Consignaciones.endpoints.api_Consignaciones import ns as namespace_Consignaciones
#from api.services.Consignaciones.endpoints.api_Consignaciones import ns as namespace_Consignaciones


def adding_end_points(blueprint, app):
    """
    Configuración de la API. Añadiendo los servicios a la página inicial
    Aquí añadir todos los servicios que se requieran para la API:
    """
    # adding the blueprint (/API_URL_PREFIX)
    api_p.init_app(blueprint)

    # adding Endpoints to this API
    # añadiendo los servicios de la API (EndPoints)
    api_p.add_namespace(namespace_Comp_Root)
    api_p.add_namespace(namespace_Comp_Leaf)
    api_p.add_namespace(namespace_Comp_Internal)
    api_p.add_namespace(namespace_Block_Leaf)
    api_p.add_namespace(namespace_Block_Root)

    # registrando las rutas:
    app.register_blueprint(blueprint)


def generate_swagger_json_file(app):
    # to generate the local copy of swagger.json
    app_cpy = copy.copy(app)
    app_cpy.config["SERVER_NAME"] = "localhost"
    app_cpy.app_context().__enter__()
    with open('swagger.json', 'w', encoding='utf-8') as outfile:
        json.dump(api_p.__schema__, outfile, indent=2, ensure_ascii=False)


def adding_blueprint_routes(blueprint):
    # this path is only for testing purposes:
    @blueprint.route("/test")
    def b_test():
        """
            To know whether the Blueprint is working or not Ex: http://127.0.0.1:5000/api/test
        """
        return "This is a test. Blueprint is working correctly."


def adding_app_routes(app):
    # @app.route("/")
    # def main_page():
    #    """ Adding initial page """
    #    return "This is home page for this API, check the pefix to see the UI"

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')


def build_app():
    # Add authentication for this API
    # add_authentication(app)

    # Path configuration:
    blueprint = Blueprint('api', __name__, url_prefix=init.API_URL_PREFIX)  # Name Space for API using Blueprint

    # blueprint for non-auth parts of app
    # from api.authentication.main import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    # from api.authentication.auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)

    adding_blueprint_routes(blueprint)  # adding normal routes to the Blueprint /API_URL_PREFIX/.. (if is needed)
    adding_end_points(blueprint, app)  # Add blueprint (API_URL_PREFIX), routes and EndPoints
    adding_app_routes(app)  # adding normal routes to the app /..
    return app


def main():

    # build the flask app (web application)
    app = build_app()

    # initializing this API
    ts = dt.datetime.now().strftime('[%Y-%b-%d %H:%M:%S.%f]')
    if init.FLASK_DEBUG:
        log.info(f'>>>>> {ts} Starting development server <<<<<')
    else:
        log.info(f'>>>>> {ts} Starting production server <<<<<')

    # serve the application
    if init.FLASK_DEBUG:
        app.run(debug=init.FLASK_DEBUG, port=5000)
    else:
        serve(app, host='0.0.0.0', port=init.PORT)


if __name__ == "__main__":
    main()
