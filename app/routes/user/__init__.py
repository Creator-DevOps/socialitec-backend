from .admin_routes import admin_routes

def register_user_routes(app):
    app.register_blueprint(admin_routes, url_prefix="/admins")
