from flask import Blueprint, request, jsonify, Response, abort, current_app
from app.utils.auth import jwt_required
from app.models.document.report import Report
from app.services.document.report_services import (
    get_reports_paginated,
    get_report_by_id,
    create_report,
    update_report,
    delete_report,
     get_report_signed_url 
)
from app.services.document.document_services import get_s3_stream_for_document

report_routes = Blueprint("report", __name__)

@report_routes.route("/", methods=["GET"])
@jwt_required
def list_reports():
    try:
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)
        search = request.args.get("search", default=None, type=str)
        if page and limit:
            result = get_reports_paginated(page, limit, search_query=search)
        else:
            total = Report.query.filter(Report.deleted_at.is_(None)).count() or 1
            result = get_reports_paginated(1, total, search_query=search)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception("Error al listar reportes")
        return jsonify({"error": str(e)}), 500

@report_routes.route("/<int:document_id>", methods=["GET"])
@jwt_required
def get_report_route(document_id):
    rpt = get_report_by_id(document_id)
    if not rpt:
        return jsonify({"message": "Reporte no encontrado"}), 404
    return jsonify(rpt), 200

@report_routes.route("/", methods=["POST"])
@jwt_required
def post_report():
    file = request.files.get("file")
    request_id = request.form.get("request_id", type=int)
    coordinator_id = request.form.get("coordinator_id", type=int)
    report_number = request.form.get("report_number", type=int)
    item_id = request.form.get("item_id", type=int)
    status = request.form.get("status", type=int, default=0)
    feedback = request.form.get("feedback", type=str)
    document_name = request.form.get("document_name", type=str)
    missing = [k for k, v in {"file": file, "request_id": request_id,"report_number":report_number, "coordinator_id": coordinator_id, "item_id": item_id}.items() if v is None]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400
    try:
        rpt = create_report(file=file, request_id=request_id,report_number=report_number, coordinator_id=coordinator_id, item_id=item_id, status=status or 0, feedback=feedback, document_name=document_name)
        return jsonify({"message": "Reporte creado", "data": rpt}), 201
    except KeyError as ke:
        return jsonify({"error": str(ke)}), 404
    except Exception as e:
        current_app.logger.exception("Error al crear reporte")
        return jsonify({"error": str(e)}), 500

@report_routes.route("/<int:document_id>", methods=["PUT"])
@jwt_required
def put_report(document_id):
    file = request.files.get("file")
    request_id = request.form.get("request_id", type=int)
    coordinator_id = request.form.get("coordinator_id", type=int)
    report_number = request.form.get("report_number",type=int)
    item_id = request.form.get("item_id", type=int)
    status = request.form.get("status", type=int)
    feedback = request.form.get("feedback", type=str)
    document_name = request.form.get("document_name", type=str)
    if not any([file, request_id is not None, report_number is not None,coordinator_id is not None, item_id is not None, status is not None, feedback is not None, document_name is not None]):
        return jsonify({"error": "Debe enviar al menos un campo a actualizar"}), 400
    try:
        updated = update_report(document_id=document_id, file=file, request_id=request_id, report_number=report_number,coordinator_id=coordinator_id, item_id=item_id, status=status, feedback=feedback, document_name=document_name)
        if not updated:
            return jsonify({"message": "Reporte no encontrado"}), 404
        return jsonify({"message": "Reporte actualizado", "data": updated}), 200
    except KeyError as ke:
        return jsonify({"error": str(ke)}), 404
    except Exception as e:
        current_app.logger.exception("Error al actualizar reporte")
        return jsonify({"error": str(e)}), 500

@report_routes.route("/<int:document_id>", methods=["DELETE"])
@jwt_required
def delete_report_route(document_id):
    try:
        ok = delete_report(document_id)
        if not ok:
            return jsonify({"message": "Reporte no encontrado"}), 404
        return jsonify({"message": "Reporte eliminado"}), 200
    except Exception as e:
        current_app.logger.exception("Error al eliminar reporte")
        return jsonify({"error": str(e)}), 500

@report_routes.route("/<int:document_id>/download", methods=["GET"])
@jwt_required
def download_report(document_id):
    result = get_s3_stream_for_document(document_id)
    if not result:
        abort(404, description="Reporte no encontrado")
    stream, content_type, filename = result
    return Response(stream.read(), mimetype=content_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@report_routes.route("/<int:document_id>/signed-url", methods=["GET"])
@jwt_required
def signed_url_report(document_id: int):
    url = get_report_signed_url(document_id)
    return jsonify({ "url": url }), 200