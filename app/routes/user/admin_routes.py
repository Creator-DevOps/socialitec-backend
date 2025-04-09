from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.user.admin_services import (
    get_all_admins,
    get_admin_by_id,
    create_admin,
    update_admin,
    delete_admin,
    get_admins_paginated
)
# Importas las documentaciones
from .admin_swagger import (
    get_admins_doc,
    get_admin_doc,
    create_admin_doc,
    update_admin_doc,
    delete_admin_doc
)

admin_routes = Blueprint("admin", __name__)

#Ruta para obtener todos los administradores
@admin_routes.route("/", methods=["GET"])
def get_admins():
    try:
        # Lee los parámetros si vienen
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)

        if page and limit:
            result = get_admins_paginated(page, limit)
        else:
            admins = get_all_admins()
            result = {
                "items": admins,
                "total": len(admins),
                "page": 1,
                "limit": len(admins),
                "pages": 1
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "No se pudo obtener la lista de administradores",
            "details": str(e)
        }), 500
    

#Obtener un administrador por su id
@admin_routes.route("/<int:user_id>", methods=["GET"])
def get_admin(user_id):
    try:
        admin = get_admin_by_id(user_id)
        if not admin:
            return jsonify({"message": "Administrador no encontrado"}), 404
        return jsonify({"message": "Administrador encontrado", "data": admin}), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener administrador", "details": str(e)}), 500

#Crear a un nuevo administrador
@admin_routes.route("/", methods=["POST"])
def create_admin_route():
    data = request.get_json()
    required = ["name", "email", "password", "position"]
    missing = [f for f in required if not data.get(f)]

    if missing:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}"}), 400

    try:
        new_admin = create_admin(data)
        return jsonify({"message": "Administrador creado", "data": new_admin}), 201
    except Exception as e:
        return jsonify({"error": "No se pudo crear el administrador", "details": str(e)}), 500

#Actualziar administrador
@admin_routes.route("/<int:user_id>", methods=["PUT"])
def update_admin_route(user_id):
    data = request.get_json()
    try:
        updated = update_admin(user_id, data)
        if not updated:
            return jsonify({"message": "Administrador no encontrado"}), 404
        return jsonify({"message": "Administrador actualizado", "data": updated}), 200
    except Exception as e:
        return jsonify({"error": "Error al actualizar", "details": str(e)}), 500


#Eliminar administrador
@admin_routes.route("/<int:user_id>", methods=["DELETE"])
def delete_admin_route(user_id):
    try:
        deleted = delete_admin(user_id)
        if not deleted:
            return jsonify({"message": "Administrador no encontrado"}), 404
        return jsonify({"message": "Administrador eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar", "details": str(e)}), 500
    

# Documentación de las rutas
get_admins.__doc__       = get_admins_doc
get_admin.__doc__        = get_admin_doc
create_admin_route.__doc__ = create_admin_doc
update_admin_route.__doc__ = update_admin_doc
delete_admin_route.__doc__ = delete_admin_doc

