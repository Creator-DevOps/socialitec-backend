from .request_routes import request_routes


def register_request_routes(app):
    app.register_blueprint(request_routes, url_prefix="/requests")


