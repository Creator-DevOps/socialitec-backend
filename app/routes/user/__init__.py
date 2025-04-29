from .admin_routes import admin_routes
from .student_routes import student_routes
from .coordinator_routes import coordinator_routes
from .auth_routes import auth_routes

def register_user_routes(app):
    app.register_blueprint(admin_routes, url_prefix="/admins")
    app.register_blueprint(student_routes, url_prefix="/students")
    app.register_blueprint(coordinator_routes, url_prefix="/coordinators")
    app.register_blueprint(auth_routes, url_prefix="/")
