from flask import Blueprint, jsonify, request
from app.utils.auth import jwt_required
from app.services.user.student_services import (
    get_all_students,
    get_student_by_id,
    create_student,
    update_student,
    delete_student,
    get_students_paginated
)

student_routes = Blueprint("student", __name__)

# Obtener todos los estudiantes
@student_routes.route("/", methods=["GET"])
@jwt_required
def get_students():
    try:
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)
        query = request.args.get("query", default=None, type=str)

        if page and limit:
            result = get_students_paginated(page, limit, search_query=query)
        else:
            students = get_all_students()
            result = {
                "items": students,
                "total": len(students),
                "page": 1,
                "limit": len(students),
                "pages": 1
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "No se pudo obtener la lista de estudiantes",
            "details": str(e)
        }), 500

# Obtener un estudiante por ID
@student_routes.route("/<int:user_id>", methods=["GET"])
@jwt_required
def get_student(user_id):
    try:
        student = get_student_by_id(user_id)
        if not student:
            return jsonify({"message": "Estudiante no encontrado"}), 404
        return jsonify({"message": "Estudiante encontrado", "data": student}), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener estudiante", "details": str(e)}), 500

# Crear estudiante
@student_routes.route("/", methods=["POST"])
@jwt_required
def create_student_route():
    data = request.get_json()
    required = ["name", "email", "password", "control_number"]
    missing = [f for f in required if not data.get(f)]

    if missing:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}"}), 400

    try:
        new_student = create_student(data)
        return jsonify({"message": "Estudiante creado", "data": new_student}), 201
    except Exception as e:
        return jsonify({"error": "No se pudo crear el estudiante", "details": str(e)}), 500

# Actualizar estudiante
@student_routes.route("/<int:user_id>", methods=["PUT"])
@jwt_required
def update_student_route(user_id):
    data = request.get_json()
    try:
        updated = update_student(user_id, data)
        if not updated:
            return jsonify({"message": "Estudiante no encontrado"}), 404
        return jsonify({"message": "Estudiante actualizado", "data": updated}), 200
    except Exception as e:
        return jsonify({"error": "Error al actualizar", "details": str(e)}), 500

# Eliminar estudiante
@student_routes.route("/<int:user_id>", methods=["DELETE"])
@jwt_required
def delete_student_route(user_id):
    try:
        deleted = delete_student(user_id)
        if not deleted:
            return jsonify({"message": "Estudiante no encontrado"}), 404
        return jsonify({"message": "Estudiante eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar", "details": str(e)}), 500
