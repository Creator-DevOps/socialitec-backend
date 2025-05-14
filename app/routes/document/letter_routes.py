# app/routes/letter_routes.py

import os
from flask import Blueprint, request, jsonify, Response, abort, current_app
from app.utils.auth import jwt_required
from app.models.document.release_letter import ReleaseLetter

from app.services.document.letter_services import (
    get_all_letters,
    get_letters_paginated,
    get_letter_by_id,
    create_release_letter,
    update_release_letter,
    delete_release_letter,
    get_letter_signed_url
)
from app.services.document.document_services import get_s3_stream_for_document

letter_routes = Blueprint("letter", __name__)

@letter_routes.route("/", methods=["GET"])
@jwt_required
def list_letters():
    try:
        page   = request.args.get("page",  type=int)
        limit  = request.args.get("limit", type=int)
        search = request.args.get("search", default=None, type=str)

        if page and limit:
            result = get_letters_paginated(page=page, limit=limit, search_query=search)
        else:
            total = ReleaseLetter.query.filter(ReleaseLetter.deleted_at.is_(None)).count() or 1
            result = get_letters_paginated(page=1, limit=total, search_query=search)

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.exception("Error al listar cartas de liberación")
        return jsonify({"error": str(e)}), 500

@letter_routes.route("/<int:document_id>", methods=["GET"])
@jwt_required
def get_letter(document_id: int):
    letter = get_letter_by_id(document_id)
    if not letter:
        return jsonify({"message": "ReleaseLetter no encontrado"}), 404
    return jsonify(letter), 200

@letter_routes.route("/", methods=["POST"])
@jwt_required
def post_letter():
    file           = request.files.get("file")
    request_id     = request.form.get("request_id",     type=int)
    coordinator_id = request.form.get("coordinator_id", type=int)
    document_name  = request.form.get("document_name",  type=str)

    missing = [k for k, v in {
        "file": file,
        "request_id": request_id,
        "coordinator_id": coordinator_id
    }.items() if v is None]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

    try:
        letter = create_release_letter(
            file,
            request_id,
            coordinator_id,
            document_name=document_name
        )
        return jsonify({"message": "ReleaseLetter created", "data": letter}), 201

    except KeyError as ke:
        return jsonify({"error": str(ke)}), 404
    except Exception as e:
        current_app.logger.exception("Error al crear carta de liberación")
        return jsonify({"error": str(e)}), 500

@letter_routes.route("/<int:document_id>", methods=["PUT"])
@jwt_required
def put_letter(document_id: int):
    file           = request.files.get("file")
    coordinator_id = request.form.get("coordinator_id", type=int)
    document_name  = request.form.get("document_name",  type=str)

    if not any([file, coordinator_id is not None, document_name is not None]):
        return jsonify({"error": "Debe enviar al menos 'file', 'coordinator_id' o 'document_name'"}), 400

    try:
        updated = update_release_letter(
            document_id,
            file=file,
            coordinator_id=coordinator_id,
            document_name=document_name
        )
        if not updated:
            return jsonify({"message": "ReleaseLetter no encontrado"}), 404
        return jsonify({"message": "ReleaseLetter updated", "data": updated}), 200

    except KeyError as ke:
        return jsonify({"error": str(ke)}), 404
    except Exception as e:
        current_app.logger.exception("Error al actualizar carta de liberación")
        return jsonify({"error": str(e)}), 500

@letter_routes.route("/<int:document_id>", methods=["DELETE"])
@jwt_required
def remove_letter(document_id: int):
    try:
        ok = delete_release_letter(document_id)
        if not ok:
            return jsonify({"message": "ReleaseLetter no encontrado"}), 404
        return jsonify({"message": "ReleaseLetter deleted"}), 200

    except Exception as e:
        current_app.logger.exception("Error al eliminar carta de liberación")
        return jsonify({"error": str(e)}), 500

@letter_routes.route("/<int:document_id>/download", methods=["GET"])
@jwt_required
def download_letter(document_id: int):
    result = get_s3_stream_for_document(document_id)
    if not result:
        abort(404, description="ReleaseLetter not found")
    stream, content_type, filename = result
    return Response(
        stream.read(),
        mimetype=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@letter_routes.route("/<int:document_id>/signed-url", methods=["GET"])
@jwt_required
def signed_url_letter(document_id: int):
    url = get_letter_signed_url(document_id)
    return jsonify({"url": url}), 200
