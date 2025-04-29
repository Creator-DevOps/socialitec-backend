from .home import home_bp
from .user import register_user_routes
from .institution import register_institution_routes

def register_blueprints(app):
    app.register_blueprint(home_bp)         
    register_user_routes(app)    
    register_institution_routes(app)           
