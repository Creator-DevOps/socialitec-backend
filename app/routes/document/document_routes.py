# app/routes/document_routes.py
from flask import Blueprint, request, jsonify
from app.utils.auth    import jwt_required
from app.services.document.document_services import (
    get_all_documents,
    get_document_by_id,
    create_document,
    delete_document
)

document_routes = Blueprint("document", __name__)

@document_routes.route("/", methods=["GET"])
@jwt_required
def list_documents():
    return jsonify(get_all_documents()), 200

@document_routes.route("/<int:document_id>", methods=["GET"])
@jwt_required
def get_document(doc_id):
    doc = get_document_by_id(doc_id)
    if not doc:
        return jsonify({"message":"Document not found"}), 404
    return jsonify(doc), 200

@document_routes.route("/", methods=["POST"])
@jwt_required
def post_document():
    file = request.files.get("file")
    dtype = request.form.get("document_type", type=int)
    if not file or dtype is None:
        return jsonify({"error":"file and document_type are required"}), 400
    result = create_document(file, document_type=dtype)
    return jsonify(result), 201

@document_routes.route("/<int:document_id>", methods=["DELETE"])
@jwt_required
def remove_document(doc_id):
    ok = delete_document(doc_id)
    if not ok:
        return jsonify({"message":"Document not found"}), 404
    return jsonify({"message":"Document deleted"}), 200
