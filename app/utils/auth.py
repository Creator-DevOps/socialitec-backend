#Middleware to JWT
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

# Middleware para proteger rutas
def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({"error": "Unauthorized Token", "details": str(e)}), 401
        return fn(*args, **kwargs)
    return wrapper

# Función para obtener usuario actual
def get_current_user():
    user_id = get_jwt_identity()
    return user_id
