from flask import Blueprint, jsonify, request
from app.utils.auth import jwt_required
from app.services.institution.institution_services import (
    get_all_institutions,
    get_institution_by_id,
    create_institution,
    update_institution,
    delete_institution,
    get_institutions_paginated
)

institution_routes = Blueprint("institution", __name__)

# Obtener todas las instituciones
@institution_routes.route("/", methods=["GET"])
@jwt_required
def get_institutions():
    try:
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)
        query = request.args.get("query", default=None, type=str)

        if page and limit:
            result = get_institutions_paginated(page, limit, search_query=query)
        else:
            institutions = get_all_institutions()
            result = {
                "items": institutions,
                "total": len(institutions),
                "page": 1,
                "limit": len(institutions),
                "pages": 1
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "No se pudo obtener la lista de instituciones", "details": str(e)}), 500

# Obtener institución por ID
@institution_routes.route("/<int:institution_id>", methods=["GET"])
@jwt_required
def get_institution(institution_id):
    try:
        institution = get_institution_by_id(institution_id)
        if not institution:
            return jsonify({"message": "Institución no encontrada"}), 404
        return jsonify({"message": "Institución encontrada", "data": institution}), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener institución", "details": str(e)}), 500

# Crear institución
@institution_routes.route("/", methods=["POST"])
@jwt_required
def create_institution_route():
    data = request.get_json()
    required = ["institution_name", "email"]
    missing = [f for f in required if not data.get(f)]

    if missing:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}"}), 400

    try:
        new_institution = create_institution(data)
        return jsonify({"message": "Institución creada", "data": new_institution}), 201
    except Exception as e:
        return jsonify({"error": "No se pudo crear la institución", "details": str(e)}), 500

# Actualizar institución
@institution_routes.route("/<int:institution_id>", methods=["PUT"])
@jwt_required
def update_institution_route(institution_id):
    data = request.get_json()
    try:
        updated = update_institution(institution_id, data)
        if not updated:
            return jsonify({"message": "Institución no encontrada"}), 404
        return jsonify({"message": "Institución actualizada", "data": updated}), 200
    except Exception as e:
        return jsonify({"error": "Error al actualizar institución", "details": str(e)}), 500

# Eliminar institución
@institution_routes.route("/<int:institution_id>", methods=["DELETE"])
@jwt_required
def delete_institution_route(institution_id):
    try:
        deleted = delete_institution(institution_id)
        if not deleted:
            return jsonify({"message": "Institución no encontrada"}), 404
        return jsonify({"message": "Institución eliminada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar institución", "details": str(e)}), 500
