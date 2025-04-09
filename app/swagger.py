from flasgger import Swagger

swagger_template = {
    "info": {
        "title": "Socialitec API",
        "description": "Documentación de la API para Socialitec",
        "version": "1.0.0",
    },
    "basePath": "/",
    
}

# Definición de la configuración Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "socialitec",
            "route": "/socialitec.json",
            "rule_filter": lambda rule: True,  # Incluye todas las rutas
            "model_filter": lambda tag: True,  # Incluye todos los modelos
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}

def init_swagger(app):
    Swagger(app, template=swagger_template, config=swagger_config)
