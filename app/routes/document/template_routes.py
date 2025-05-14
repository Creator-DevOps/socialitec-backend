import os
from flask import Blueprint, request, jsonify, Response, abort, current_app
from app.utils.auth import jwt_required
from app.models.document.template import Template
from app.services.document.template_services import (
    get_all_templates,
    get_template_by_id,
    create_template,
    update_template,
    delete_template,
    get_templates_paginated,
    get_template_signed_url
)
from app.services.document.document_services import get_s3_stream_for_document

template_routes = Blueprint("template", __name__)

@template_routes.route("/<int:template_id>/signed-url", methods=["GET"])
@jwt_required
def signed_url(template_id: int):
    url = get_template_signed_url(template_id)
    return jsonify({ "url": url }), 200

@template_routes.route("/", methods=["GET"])
@jwt_required
def list_templates():
    try:
        page  = request.args.get("page",  type=int)
        limit = request.args.get("limit", type=int)
        query = request.args.get("query", default=None, type=str)

        if page and limit:
            result = get_templates_paginated(page, limit, search_query=query)
        else:
            total = Template.query.filter(Template.deleted_at.is_(None)).count() or 1
            result = get_templates_paginated(1, total, search_query=query)

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.exception("Error al listar plantillas")
        return jsonify({"error": str(e)}), 500


@template_routes.route("/<int:template_id>", methods=["GET"])
@jwt_required
def get_template(template_id):
    template = get_template_by_id(template_id)
    if not template:
        return jsonify({"message":"Template not found"}), 404
    return jsonify(template), 200


@template_routes.route("/", methods=["POST"])
@jwt_required
def post_template():
    file = request.files.get("file")
    description   = request.form.get("description")
    coordinator_id= request.form.get("coordinator_id", type=int)
    document_name = request.form.get("document_name")

    # Validaciones
    missing = []
    if not file:              missing.append("file")
    if not description:       missing.append("description")
    if not coordinator_id:    missing.append("coordinator_id")
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

    # Validar coordinador
    from app.models.user.coordinator import Coordinator
    coord = Coordinator.query.filter_by(user_id=coordinator_id, deleted_at=None).first()
    if not coord:
        return jsonify({"error": f"Coordinador {coordinator_id} no existe"}), 400

    try:
        template = create_template(
            file,
            description,
            coordinator_id,
            document_name=document_name
        )
        return jsonify({"message":"Plantilla creada","data":template}), 201
    except Exception as e:
        current_app.logger.exception("Error al crear plantilla")
        return jsonify({"error": str(e)}), 500


@template_routes.route("/<int:template_id>", methods=["PUT"])
@jwt_required
def put_template(template_id):
    file = request.files.get("file")
    description    = request.form.get("description")
    coordinator_id = request.form.get("coordinator_id", type=int)
    document_name  = request.form.get("document_name")

    if not file and description is None and coordinator_id is None and document_name is None:
        return jsonify({"error": "Debe enviar al menos 'file', 'description', 'coordinator_id' o 'document_name'"}), 400

    try:
        updated = update_template(
            template_id,
            file=file,
            description=description,
            coordinator_id=coordinator_id,
            document_name=document_name
        )
        if not updated:
            return jsonify({"message": "Template not found"}), 404

        return jsonify({"message": "Template updated", "data": updated}), 200

    except Exception as e:
        current_app.logger.exception("Error al actualizar plantilla")
        return jsonify({"error": str(e)}), 500


@template_routes.route("/<int:template_id>", methods=["DELETE"])
@jwt_required
def remove_template(template_id):
    ok = delete_template(template_id)
    if not ok:
        return jsonify({"message":"Template not found"}), 404
    return jsonify({"message":"Template deleted"}), 200


@template_routes.route("/<int:template_id>/download", methods=["GET"])
@jwt_required
def download_template(template_id):
    result = get_s3_stream_for_document(template_id)
    if result is None:
        abort(404, description="Template not found")

    stream, content_type, filename = result
    return Response(
        stream.read(),
        mimetype=content_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
    )
