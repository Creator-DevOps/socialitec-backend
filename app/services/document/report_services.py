from datetime import datetime
db = None  # placeholder for actual import
from app.extensions import db
from sqlalchemy import desc
from app.models.document.report import Report
from app.models.document.document import Document
from app.services.document.document_services import (
    create_document,
    update_document,
    get_document_by_id,
)
from app.models.request.request import Request
from app.models.user.user import User
from app.models.user.student import Student
from sqlalchemy import or_
from app.services.request.request_services import get_request_by_id
from math import ceil
import os
from datetime import datetime
from urllib.parse import urlparse
from flask import abort
from app.extensions import db, s3_client

BUCKET     = os.getenv("S3_BUCKET_NAME")
EXPIRES_IN = 3600  # segundos

# New import for cycle-item
from app.models.document.report_cycle_item import ReportCycleItem


def format_report(report: Report) -> dict:
    doc = get_document_by_id(report.document_id)
    req = get_request_by_id(report.request_id)
    return {
        "document_id": report.document_id,
        "document_name": doc.get("document_name"),
        "item_id": report.item_id,
        "request": req,
        "coordinator_id": report.coordinator_id,
        "report_number": report.report_number,
        "status": report.status,
        "feedback": report.feedback,
        "file_path": doc.get("file_path"),
        "document_type": doc.get("document_type"),
        "created_at": report.created_at.isoformat(),
        "updated_at": report.updated_at.isoformat() if report.updated_at else None
    }


def get_all_reports() -> list[dict]:
    reps = Report.query.filter(Report.deleted_at.is_(None)).all()
    return [format_report(r) for r in reps]


def get_reports_paginated(page: int = 1, limit: int = 10, search_query: str = None) -> dict:
    query = (
         Report.query
        .join(Document, Report.document_id == Document.document_id)
        .join(Request,  Report.request_id  == Request.request_id)
        .join(Request.student)
        .filter(Report.deleted_at.is_(None))
    )
    if search_query:
        pat = f"%{search_query}%"
        query = query.filter(
            or_( Report.feedback.ilike(pat),
                Document.document_name.ilike(pat),
                Student.control_number.ilike(pat))
        )
    total = query.count()
    recs = (
        query.order_by(Report.created_at.desc())
             .offset((page - 1) * limit)
             .limit(limit)
             .all()
    )
    items = [format_report(r) for r in recs]
    pages = ceil(total / limit) if total else 1
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}


def get_report_by_id(document_id: int) -> dict | None:
    r = Report.query.filter_by(document_id=document_id, deleted_at=None).first()
    return format_report(r) if r else None


def create_report(
    file,
    request_id: int,
    coordinator_id: int,
    report_number:int,
    item_id: int,
    status: int = 0,
    feedback: str = None,
    document_name: str = None
) -> dict:
    # Validate request
    item = ReportCycleItem.query.get(item_id)
    req = get_request_by_id(request_id)
    if not req:
        raise KeyError(f"Solicitud {request_id} no existe")
    student_name_folder = req["student"]["name"]
    if not item:
        raise KeyError(f"Ítem {item_id} no existe")
    # Build S3 prefix
    cycle_folder = item.cycle.folder_name
    # report_num = item.report_number
    prefix = f"documents/reports/{cycle_folder}/{student_name_folder}/"
    doc = create_document(file, document_type=0, key_prefix=prefix, document_name=document_name)
    report = Report(
        document_id=doc["document_id"],
        item_id=item_id,
        request_id=request_id,
        coordinator_id=coordinator_id,
        report_number=report_number,
        status=status,
        feedback=feedback
    )
    db.session.add(report)
    db.session.commit()
    return format_report(report)


def update_report(
    document_id: int,
    file=None,
    request_id: int = None,
    coordinator_id: int = None,
    report_number:int=None,
    item_id: int = None,
    status: int = None,
    feedback: str = None,
    document_name: str = None
) -> dict | None:
    # 1) Busca el report existente
    report = Report.query.filter_by(document_id=document_id, deleted_at=None).first()
    if not report:
        return None

    # 2) Si cambia la solicitud, extrae el nuevo student_name_folder
    if request_id and request_id != report.request_id:
        req = get_request_by_id(request_id)
        if not req:
            raise KeyError(f"Solicitud {request_id} no existe")
        report.request_id = request_id
        student_name_folder = req["student"]["name"]
    else:
        # si no cambió la solicitud, recupera el nombre del student actual
        current_req = get_request_by_id(report.request_id)
        student_name_folder = current_req["student"]["name"]

    # 3) Si cambia el ítem, actualiza item_id 
    if item_id and item_id != report.item_id:
        item = ReportCycleItem.query.get(item_id)
        if not item:
            raise KeyError(f"Ítem {item_id} no existe")
        report.item_id       = item_id
    else:
        item = ReportCycleItem.query.get(report.item_id)
    
    if report_number is not None:
        report.report_number = report_number
    if coordinator_id is not None:
        report.coordinator_id = coordinator_id
    if status is not None:
        report.status = status
    if feedback is not None:
        report.feedback = feedback

    report.updated_at = datetime.utcnow()
    db.session.commit()

    # 5) Reemplazo de archivo en S3 si se envía uno nuevo
    if file or document_name is not None:
        # Calcula de nuevo el folder del ciclo
        cycle_folder = item.cycle.folder_name
        report_number   = report_number
        prefix = (
            f"documents/reports/"
            f"{cycle_folder}/"
            f"{student_name_folder}/"
            f"{report.request_id}/"
            f"{report.report_number}/"
        )
        update_document(
            document_id,
            file=file,
            key_prefix=prefix,
            document_name=document_name
        )

    # 6) Devuelve el formato estandarizado
    return format_report(report)



def delete_report(document_id: int) -> bool:
    report = Report.query.filter_by(document_id=document_id, deleted_at=None).first()
    if not report:
        return False
    report.deleted_at = datetime.utcnow()
    db.session.commit()
    return True

def get_reports_by_item(item_id: int) -> list[dict]:
    reps = (
        Report.query
              .filter(Report.deleted_at.is_(None), Report.item_id == item_id)
              .all()
    )
    return [format_report(r) for r in reps]

def get_reports_by_item_paginated(
    item_id: int,
    page: int = 1,
    limit: int = 10,
    search: str = None
) -> dict:
    # 1) Traer todos los reportes para este item_id (activos)
    all_recs = (
        Report.query
              .filter(Report.deleted_at.is_(None),
                      Report.item_id == item_id)
              .order_by(desc(Report.created_at))
              .all()
    )

    # 2) Formatear TODOS a dict
    all_items = [format_report(r) for r in all_recs]

    # 3) Si hay búsqueda, filtrar en Python
    if search:
        term = search.lower()
        def matches(rep: dict) -> bool:
            stu = rep["request"]["student"]
            return (
                term in stu["control_number"].lower()
                or term in stu["name"].lower()
            )
        all_items = [rep for rep in all_items if matches(rep)]

    # 4) Paginación
    total = len(all_items)
    start = (page - 1) * limit
    end   = start + limit
    page_items = all_items[start:end]

    pages = ceil(total / limit) if total else 1

    return {
        "items": page_items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


def get_report_signed_url(document_id: int) -> str:
    """
    Genera un URL pre-firmado para un reporte dado.
    """
    # 1) Validar que el reporte exista
    report = Report.query.filter_by(document_id=document_id, deleted_at=None).first()
    if not report:
        abort(404, description="Reporte no encontrado")

    # 2) Recuperar metadata del documento
    doc = get_document_by_id(document_id)
    if not doc or not doc.get("file_path"):
        abort(404, description="Archivo del reporte no encontrado")

    # 3) Obtener la key a partir de la URL pública
    public_url = doc["file_path"]
    parsed     = urlparse(public_url)
    key        = parsed.path.lstrip("/")

    # 4) Generar presigned URL
    try:
        presigned = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=EXPIRES_IN,
        )
        return presigned
    except Exception as e:
        abort(500, description=f"Error generando presigned URL: {e}")