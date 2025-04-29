from flask import Blueprint, jsonify, request
from app.utils.auth import jwt_required
from app.services.institution.program_services import (
    get_all_programs,
    get_program_by_id,
    create_program,
    update_program,
    delete_program,
    get_programs_paginated
)

program_routes = Blueprint("program", __name__)

# Obtener todos los programas
@program_routes.route("/", methods=["GET"])
@jwt_required
def get_programs():
    try:
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)
        query = request.args.get("query", default = None, type=str)

        if page and limit:
            result = get_programs_paginated(page, limit, search_query=query)
        else:
            programs = get_all_programs()
            result = {
                "items": programs,
                "total": len(programs),
                "page": 1,
                "limit": len(programs),
                "pages": 1
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "No se pudo obtener la lista de programas", "details": str(e)}), 500

# Obtener programa por ID
@program_routes.route("/<int:program_id>", methods=["GET"])
@jwt_required
def get_program(program_id):
    try:
        program = get_program_by_id(program_id)
        if not program:
            return jsonify({"message": "Programa no encontrado"}), 404
        return jsonify({"message": "Programa encontrado", "data": program}), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener programa", "details": str(e)}), 500

# Crear programa
@program_routes.route("/", methods=["POST"])
@jwt_required
def create_program_route():
    data = request.get_json()
    required = ["institution_id", "program_name"]
    missing = [f for f in required if not data.get(f)]

    if missing:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}"}), 400

    try:
        new_program = create_program(data)
        return jsonify({"message": "Programa creado", "data": new_program}), 201
    except Exception as e:
        return jsonify({"error": "No se pudo crear el programa", "details": str(e)}), 500

# Actualizar programa
@program_routes.route("/<int:program_id>", methods=["PUT"])
@jwt_required
def update_program_route(program_id):
    data = request.get_json()
    try:
        updated = update_program(program_id, data)
        if not updated:
            return jsonify({"message": "Programa no encontrado"}), 404
        return jsonify({"message": "Programa actualizado", "data": updated}), 200
    except Exception as e:
        return jsonify({"error": "Error al actualizar programa", "details": str(e)}), 500

# Eliminar programa
@program_routes.route("/<int:program_id>", methods=["DELETE"])
@jwt_required
def delete_program_route(program_id):
    try:
        deleted = delete_program(program_id)
        if not deleted:
            return jsonify({"message": "Programa no encontrado"}), 404
        return jsonify({"message": "Programa eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar programa", "details": str(e)}), 500
