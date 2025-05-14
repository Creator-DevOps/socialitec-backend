# app/services/document/letter_services.py

from datetime import datetime
from math import ceil
from urllib.parse import urlparse
import os

from flask import abort
from app.extensions import db, s3_client
from sqlalchemy import or_
from app.models.request.request import Request
from app.models.user.student import Student
from app.models.user.user import User
from app.models.document.release_letter import ReleaseLetter
from app.models.document.document import Document
from app.services.document.document_services import (
    create_document,
    update_document,
    get_document_by_id
)
from app.services.request.request_services import get_request_by_id

BUCKET     = os.getenv("S3_BUCKET_NAME")
EXPIRES_IN = 3600  # segundos

def format_release_letter(letter: ReleaseLetter) -> dict:
    doc = get_document_by_id(letter.document_id)
    req = get_request_by_id(letter.request_id)
    return {
        "document_id":    letter.document_id,
        "document_name":  doc.get("document_name"),
        "document_type":  doc.get("document_type"),
        "request":        req,
        "coordinator_id": letter.coordinator_id,
        "file_path":      doc.get("file_path"),
        "created_at":     letter.created_at.isoformat() if letter.created_at else None,
        "updated_at":     letter.updated_at.isoformat() if letter.updated_at else None
    }

def get_all_letters() -> list[dict]:
    letters = ReleaseLetter.query.filter(ReleaseLetter.deleted_at.is_(None)).all()
    return [format_release_letter(l) for l in letters]

def get_letters_paginated(
    page: int = 1,
    limit: int = 10,
    search_query: str = None
) -> dict:
    query = (
        ReleaseLetter.query
        .join(Document, ReleaseLetter.document_id == Document.document_id)
        .join(Request, ReleaseLetter.request_id == Request.request_id)
        .join(Request.student)
        .filter(ReleaseLetter.deleted_at.is_(None))
    )

    if search_query:
        pat = f"%{search_query}%"
        query = query.filter(
            or_(
                Document.document_name.ilike(pat),
                Student.control_number.ilike(pat),
                # si quieres buscar por request_id:
                ReleaseLetter.request_id == search_query
            )
        )

    total = query.count()
    recs = (
        query.order_by(ReleaseLetter.created_at.desc())
             .offset((page - 1) * limit)
             .limit(limit)
             .all()
    )
    items = [format_release_letter(l) for l in recs]
    pages = ceil(total / limit) if total else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

def get_letter_by_id(document_id: int) -> dict | None:
    letter = ReleaseLetter.query.filter_by(document_id=document_id, deleted_at=None).first()
    return format_release_letter(letter) if letter else None

def create_release_letter(
    file,
    request_id: int,
    coordinator_id: int,
    document_name: str = None
) -> dict:
    # 1) Validar existencia de la solicitud
    req = get_request_by_id(request_id)
    if not req:
        raise KeyError(f"Solicitud {request_id} no existe")
    
    student_name_folder = req["student"]["name"]

    # 2) Subir a S3
    prefix = f"documents/letters/{student_name_folder}/"
    doc = create_document(
        file,
        document_type=2,  # 2 = release_letter
        key_prefix=prefix,
        document_name=document_name
    )

    # 3) Crear entidad en BD
    letter = ReleaseLetter(
        document_id    = doc["document_id"],
        request_id     = request_id,
        coordinator_id = coordinator_id
    )
    db.session.add(letter)
    db.session.commit()

    return format_release_letter(letter)

def update_release_letter(
    document_id: int,
    file=None,
    coordinator_id: int = None,
    document_name: str = None
) -> dict | None:
    letter = ReleaseLetter.query.filter_by(document_id=document_id, deleted_at=None).first()
    if not letter:
        return None

    # 1) Actualizar metadatos
    if coordinator_id is not None:
        letter.coordinator_id = coordinator_id
    letter.updated_at = datetime.utcnow()
    db.session.commit()

    # 2) Reemplazo de archivo o nombre en S3 usando student_name_folder
    if file or document_name is not None:
        # Volver a extraer carpeta del estudiante
        req = get_request_by_id(letter.request_id)
        student_name_folder = req["student"]["name"]
        prefix = f"documents/letters/{student_name_folder}/"
        update_document(
            document_id,
            file=file,
            key_prefix=prefix,
            document_name=document_name
        )

    return format_release_letter(letter)

def delete_release_letter(document_id: int) -> bool:
    letter = ReleaseLetter.query.filter_by(document_id=document_id, deleted_at=None).first()
    if not letter:
        return False
    letter.deleted_at = datetime.utcnow()
    db.session.commit()
    return True

def get_letter_signed_url(document_id: int) -> str:
    """
    Genera un URL prefirmado para una carta de liberación dada.
    """
    # 1) Validar existencia
    letter = ReleaseLetter.query.filter_by(document_id=document_id, deleted_at=None).first()
    if not letter:
        abort(404, description="ReleaseLetter no encontrado")

    # 2) Metadata de S3
    doc = get_document_by_id(document_id)
    if not doc or not doc.get("file_path"):
        abort(404, description="Archivo de ReleaseLetter no encontrado")

    public_url = doc["file_path"]
    parsed     = urlparse(public_url)
    key        = parsed.path.lstrip("/")

    # 3) Generar presigned URL
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=EXPIRES_IN,
        )
    except Exception as e:
        abort(500, description=f"Error generando presigned URL: {e}")
