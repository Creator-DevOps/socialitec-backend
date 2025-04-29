from .institution_routes import institution_routes
from .program_routes import program_routes


def register_institution_routes(app):
    app.register_blueprint(institution_routes, url_prefix="/institutions")
    app.register_blueprint(program_routes, url_prefix="/programs")

