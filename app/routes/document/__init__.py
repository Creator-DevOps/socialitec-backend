from .document_routes import document_routes
from .template_routes import template_routes
from .report_routes import report_routes
from .letter_routes import letter_routes
from .report_cycle_routes import report_cycle_routes


def register_document_routes(app):
    app.register_blueprint(document_routes, url_prefix="/documents")
    app.register_blueprint(template_routes, url_prefix="/templates")
    app.register_blueprint(report_routes, url_prefix="/reports")
    app.register_blueprint(letter_routes, url_prefix="/letters")
    app.register_blueprint(report_cycle_routes, url_prefix="/report_cycles")


