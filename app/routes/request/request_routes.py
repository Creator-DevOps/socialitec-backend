from flask import Blueprint, jsonify, request
from app.utils.auth import jwt_required
from app.services.request.request_services import (
    get_all_requests,
    get_request_by_id,
    get_request_by_id_user,
    create_request,
    update_request,
    delete_request,
    get_requests_paginated
)

request_routes = Blueprint("request", __name__)

# Obtener todas las solicitudes
@request_routes.route("/", methods=["GET"])
@jwt_required
def get_requests():
    try:
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)
        query = request.args.get("query", default=None, type=str)

        if page and limit:
            result = get_requests_paginated(page, limit, search_query=query)
        else:
            items = get_all_requests()
            result = {
                "items": items,
                "total": len(items),
                "page": 1,
                "limit": len(items),
                "pages": 1
            }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "No se pudo obtener la lista de solicitudes", "details": str(e)}), 500

# Obtener solicitud por ID
@request_routes.route("/<int:request_id>", methods=["GET"])
@jwt_required
def get_request(request_id):
    try:
        req = get_request_by_id(request_id)
        if not req:
            return jsonify({"message": "Solicitud no encontrada"}), 404
        return jsonify({"message": "Solicitud encontrada", "data": req}), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener solicitud", "details": str(e)}), 500

# Obtener solicitud por ID usuario
@request_routes.route("/user/<int:student_id>", methods=["GET"])
@jwt_required
def get_request_user(student_id):
    try:
        req = get_request_by_id_user(student_id)
        # if not req:
        #     return jsonify({"message": "Solicitud no encontrada"}), 404
        return jsonify({"message": "Solicitud encontrada", "data": req}), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener solicitud", "details": str(e)}), 500

# Crear solicitud
@request_routes.route("/", methods=["POST"])
@jwt_required
def create_request_route():
    data = request.get_json()
    required = ["student_id", "program_id"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}"}), 400
    try:
        new_req = create_request(data)
        return jsonify({"message": "Solicitud creada", "data": new_req}), 201
    except Exception as e:
        return jsonify({"error": "No se pudo crear la solicitud", "details": str(e)}), 500

# Actualizar solicitud
@request_routes.route("/<int:request_id>", methods=["PUT"])
@jwt_required
def update_request_route(request_id):
    data = request.get_json()
    try:
        updated = update_request(request_id, data)
        if not updated:
            return jsonify({"message": "Solicitud no encontrada"}), 404
        return jsonify({"message": "Solicitud actualizada", "data": updated}), 200
    except Exception as e:
        return jsonify({"error": "Error al actualizar solicitud", "details": str(e)}), 500

# Eliminar solicitud
@request_routes.route("/<int:request_id>", methods=["DELETE"])
@jwt_required
def delete_request_route(request_id):
    try:
        deleted = delete_request(request_id)
        if not deleted:
            return jsonify({"message": "Solicitud no encontrada"}), 404
        return jsonify({"message": "Solicitud eliminada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar solicitud", "details": str(e)}), 500
