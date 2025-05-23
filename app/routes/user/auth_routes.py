from flask import Blueprint, jsonify, request
from app.services.user.auth_services import login_service,change_password_service
from app.utils.auth import jwt_required, get_current_user
from app.models.user.user import User

auth_routes = Blueprint("auth", __name__)

# Login
@auth_routes.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Correo y contraseña son requeridos."}), 400

        result = login_service(email, password)
        return jsonify({"message": "Login exitoso", "data": result}), 200

    except Exception as e:
        return jsonify({"error": "Error al iniciar sesión", "details": str(e)}), 401

# Logout 
@auth_routes.route("/logout", methods=["POST"])
@jwt_required
def logout():
    return jsonify({"message": "Logout exitoso. Elimine su token en frontend."}), 200

# Ruta para obtener el usuario actual
@auth_routes.route("/me", methods=["GET"])
@jwt_required
def get_me():
    try:
        user_id = get_current_user()
        user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user_info = {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.institutional_email,
            "user_type": user.user_type
        }

        if user.user_type == 0 and user.admin:
            user_info["position"] = user.admin.position
        elif user.user_type == 1 and user.coordinator:
            user_info["departament"] = user.coordinator.departament
        elif user.user_type == 2 and user.student:
            user_info["control_number"] = user.student.control_number
            user_info["major"] = user.student.major
            user_info["semester"] = user.student.semester
            user_info["credits"] = user.student.credits

        return jsonify({"message": "Usuario actual", "data": user_info}), 200

    except Exception as e:
        return jsonify({"error": "Error al obtener usuario", "details": str(e)}), 500


@auth_routes.route("/change-password", methods=["POST"])
@jwt_required
def change_password():
    """
    Body esperado: {
      "current_password": "vieja123",
      "new_password": "nueva456"
    }
    """
    try:
        data = request.get_json() or {}
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return jsonify({"error": "Contraseña actual y nueva son requeridas."}), 400

        # El ID del usuario lo obtenemos del token
        user_id = get_current_user()

        # Llamamos al servicio
        result = change_password_service(user_id, current_password, new_password)
        return jsonify({"message": result["message"]}), 200

    except Exception as e:
        # Si el mensaje proviene de nuestra lógica, lo devolvemos; 
        # de lo contrario, mensaje genérico de error
        detail = str(e)
        status = 400 if "incorrecta" in detail or "no encontrado" in detail else 500
        return jsonify({"error": "Error al cambiar contraseña", "details": detail}), status