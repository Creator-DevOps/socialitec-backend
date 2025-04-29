from flask import Blueprint, jsonify, request
from app.utils.auth import jwt_required
from app.services.user.coordinator_services import (
    get_all_coordinators,
    get_coordinator_by_id,
    create_coordinator,
    update_coordinator,
    delete_coordinator,
    get_coordinators_paginated
)

coordinator_routes = Blueprint("coordinator", __name__)

# Obtener todos los coordinadores
@coordinator_routes.route("/", methods=["GET"])
@jwt_required
def get_coordinators():
    try:
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)
        query = request.args.get("query", default=None, type=str)

        if page and limit:
            result = get_coordinators_paginated(page, limit, search_query=query)
        else:
            coordinators = get_all_coordinators()
            result = {
                "items": coordinators,
                "total": len(coordinators),
                "page": 1,
                "limit": len(coordinators),
                "pages": 1
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "No se pudo obtener la lista de coordinadores",
            "details": str(e)
        }), 500


# Obtener coordinador por ID
@coordinator_routes.route("/<int:user_id>", methods=["GET"])
@jwt_required
def get_coordinator(user_id):
    try:
        coordinator = get_coordinator_by_id(user_id)
        if not coordinator:
            return jsonify({"message": "Coordinador no encontrado"}), 404
        return jsonify({"message": "Coordinador encontrado", "data": coordinator}), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener coordinador", "details": str(e)}), 500

# Crear coordinador
@coordinator_routes.route("/", methods=["POST"])
@jwt_required
def create_coordinator_route():
    data = request.get_json()
    required = ["name", "email", "password", "departament"]
    missing = [f for f in required if not data.get(f)]

    if missing:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}"}), 400

    try:
        new_coordinator = create_coordinator(data)
        return jsonify({"message": "Coordinador creado", "data": new_coordinator}), 201
    except Exception as e:
        return jsonify({"error": "No se pudo crear el coordinador", "details": str(e)}), 500

# Actualizar coordinador
@coordinator_routes.route("/<int:user_id>", methods=["PUT"])
@jwt_required
def update_coordinator_route(user_id):
    data = request.get_json()
    try:
        updated = update_coordinator(user_id, data)
        if not updated:
            return jsonify({"message": "Coordinador no encontrado"}), 404
        return jsonify({"message": "Coordinador actualizado", "data": updated}), 200
    except Exception as e:
        return jsonify({"error": "Error al actualizar", "details": str(e)}), 500

# Eliminar coordinador
@coordinator_routes.route("/<int:user_id>", methods=["DELETE"])
@jwt_required
def delete_coordinator_route(user_id):
    try:
        deleted = delete_coordinator(user_id)
        if not deleted:
            return jsonify({"message": "Coordinador no encontrado"}), 404
        return jsonify({"message": "Coordinador eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar", "details": str(e)}), 500
