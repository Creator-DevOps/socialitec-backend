from datetime import datetime
from app.extensions import db
import os
from urllib.parse import urlparse
from flask import abort
from app.extensions import s3_client
from app.models.document.template import Template
from app.models.document.document import Document
from sqlalchemy import or_
from app.services.document.document_services import (
    create_document,
    update_document,
    get_document_by_id
)

BUCKET = os.getenv("S3_BUCKET_NAME")
EXPIRES_IN = 3600 

def get_template_signed_url(template_id: int) -> str:
    """
    Genera un URL pre-firmado para un template dado.
    """

    tpl = get_template_by_id(template_id)
    if not tpl or not tpl.get("file_path"):
        abort(404, description="Template not found")

    public_url = tpl["file_path"]

    parsed = urlparse(public_url)
    key = parsed.path.lstrip("/") 


    try:
        presigned = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=EXPIRES_IN,
        )
        return presigned
    except Exception as e:
        abort(500, description=f"Error generating presigned URL: {e}")


def format_template(template: Template) -> dict:
    # Obtenemos metadata completa del documento
    doc = get_document_by_id(template.document_id)
    return {
        "document_id":    template.document_id,
        "document_name":  doc.get("document_name"),
        "document_type":  doc.get("document_type"),
        "description":    template.description,
        "coordinator_id": template.coordinator_id,
        "file_path": doc.get("file_path"),
        # "created_at":    template.created_at.isoformat(),
        # "updated_at":    template.updated_at.isoformat() if template.updated_at else None,
    }


def get_all_templates() -> list[dict]:
    templates = Template.query.filter(Template.deleted_at.is_(None)).all()
    return [format_template(t) for t in templates]


def get_templates_paginated(page: int = 1, limit: int = 10, search_query: str = None) -> dict:
    query = Template.query \
        .join(Document, Template.document_id == Document.document_id) \
        .filter(Template.deleted_at.is_(None))

    if search_query:
        ilike_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Template.description.ilike(ilike_pattern),
                Document.document_name.ilike(ilike_pattern)
            )
        )

    total = query.count()

    templates = (
        query
        .order_by(Template.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items = []
    for t in templates:
        doc = get_document_by_id(t.document_id)
        items.append({
            "document_id":    t.document_id,
            "document_name":  doc.get("document_name"),
            "document_type":  doc.get("document_type"),
            "description":    t.description,
            "coordinator_id": t.coordinator_id,
            "file_path":      doc.get("file_path"),
        })


    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


def get_template_by_id(template_id: int) -> dict | None:
    t = Template.query.filter_by(document_id=template_id, deleted_at=None).first()
    return format_template(t) if t else None


def create_template(file, description: str, coordinator_id: int, document_name: str = None) -> dict:
    # Creamos el Document (tipo = 1)
    prefix = f"documents/templates/{coordinator_id}/"
    doc = create_document(
         file,
         document_type=1,
         key_prefix=prefix,
         document_name=document_name
     )
    # Creamos la entidad Template
    template = Template(
        document_id    = doc["document_id"],
        description    = description,
        coordinator_id = coordinator_id
    )
    db.session.add(template)
    db.session.commit()
    return format_template(template)


def update_template(
    template_id: int,
    file=None,
    description: str = None,
    coordinator_id: int = None,
    document_name: str = None
) -> dict | None:
    template = Template.query.filter_by(
        document_id=template_id,
        deleted_at=None
    ).first()
    if not template:
        return None

    # Actualizamos campos en la tabla Template
    if description is not None:
        template.description = description
    if coordinator_id is not None:
        template.coordinator_id = coordinator_id

    template.updated_at = datetime.utcnow()
    db.session.commit()

    # Actualizamos metadata o archivo en S3 si se proporciona
    if file or document_name is not None:
        prefix = f"documents/templates/{template.coordinator_id}/"
        update_document(
            template_id,
            file=file,
            key_prefix=prefix,
            document_name=document_name
        )

    # Devolvemos la info actualizada
    return format_template(template)


def delete_template(template_id: int) -> bool:
    template = Template.query.filter_by(document_id=template_id, deleted_at=None).first()
    if not template:
        return False
    template.deleted_at = datetime.utcnow()
    db.session.commit()
    return True