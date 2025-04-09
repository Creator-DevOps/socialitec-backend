from flask import Flask
from .config import Config
from .extensions import db, migrate,jwt,cors
from .routes import register_blueprints
from flask import request, Response

def check_auth(username, password):
    """Valida si el usuario y contraseña coinciden con los valores esperados."""
    return username == "admindocsocial" and password == "admin2034ss"

def authenticate():
    """Envía una respuesta 401 que solicita autenticación."""
    return Response(
        'Acceso restringido. Por favor, autentíquese.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config['JSON_SORT_KEYS'] = False
    app.config.from_object(Config)

    #  extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints endpoints
    register_blueprints(app)

    #Swagger
    from .swagger import init_swagger
    init_swagger(app)

    @app.before_request
    def require_auth_for_swagger():
        if request.path.startswith('/docs'):
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()

    return app
