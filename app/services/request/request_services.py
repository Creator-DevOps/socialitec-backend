from app.models.request.request import Request
from app.extensions import db
from datetime import datetime
from sqlalchemy import or_
from app.models.user.user import User
from app.models.institution.program import Program
from app.models.institution.institution import Institution
from math import ceil

from app.services.user.student_services import get_student_by_id
from app.services.institution.program_services import get_program_by_id
from app.services.institution.institution_services import get_institution_by_id
# Formatear solicitud
def format_request(req):
    if not req:
        return None

    student     = get_student_by_id(req.student_id)
    program     = get_program_by_id(req.program_id)
    institution = None
    if program:
        institution = get_institution_by_id(program["institution_id"])

    return {
        "request_id":      req.request_id,
        "cycle_id":      req.cycle_id,
        "student":         student,
        "student_id":        req.student_id,
        "program":         program,
        "institution":     institution,
        "acceptance_status": req.acceptance_status,
        "progress_status":   req.progress_status,
        "completed_hours":   req.completed_hours,
        "coordinator_id":    req.coordinator_id,
        "feedback":          req.feedback,
        "created_at":        req.created_at.isoformat(),
        "updated_at":        req.updated_at.isoformat() if req.updated_at else None
    }

def get_requests_paginated(page=1, limit=10, search_query=None):
    # 1) Armar la base de la query con todos los joins
    query = (
        Request.query
        .join(User,        Request.student_id    == User.user_id)
        .join(Program,     Request.program_id    == Program.program_id)
        .join(Institution, Program.institution_id == Institution.institution_id)
        .filter(Request.deleted_at.is_(None))
    )

    # 2) Si vienen términos de búsqueda, filtrar en todos los campos deseados
    if search_query:
        pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                User.name.ilike(pattern),                  
                Program.program_name.ilike(pattern),      
                Institution.institution_name.ilike(pattern),
                Request.acceptance_status.cast(db.String).ilike(pattern),
                Request.feedback.ilike(pattern)
            )
        )

    # 3) Paginación y conteo
    total = query.count()
    results = (
        query
        .order_by(Request.request_date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items = [format_request(r) for r in results]
    pages = ceil(total / limit) if total else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }

def get_all_requests():
    recs = Request.query.filter(Request.deleted_at.is_(None)).all()
    return [format_request(r) for r in recs]

def get_request_by_id(request_id):
    req = Request.query.filter_by(request_id=request_id, deleted_at=None).first()
    return format_request(req) if req else None

def get_request_by_id_user(student_id):
    req = Request.query.filter_by(student_id=student_id, deleted_at=None).first()
    return format_request(req) if req else None

# Crear solicitud
def create_request(data):
    try:
        req = Request(
            student_id=data["student_id"],
            program_id=data["program_id"],
            cycle_id=data["cycle_id"],
            acceptance_status=data.get("acceptance_status", 0),
            progress_status=data.get("progress_status", 0),
            request_date=data.get("request_date"),
            completed_hours=data.get("completed_hours", 0),
            coordinator_id=data.get("coordinator_id"),
            feedback=data.get("feedback", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        db.session.add(req)
        db.session.commit()
        return format_request(req)
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al crear solicitud: {str(e)}")

# Actualizar solicitud
def update_request(request_id, data):
    req = Request.query.filter_by(request_id=request_id, deleted_at=None).first()
    if not req:
        return None
    try:
        req.student_id = data.get("student_id", req.student_id)
        req.program_id = data.get("program_id", req.program_id)
        req.cycle_id = data.get("cycle_id", req.cycle_id)
        req.acceptance_status = data.get("acceptance_status", req.acceptance_status)
        req.progress_status = data.get("progress_status", req.progress_status)
        req.request_date = data.get("request_date", req.request_date)
        req.completed_hours = data.get("completed_hours", req.completed_hours)
        req.coordinator_id = data.get("coordinator_id", req.coordinator_id)
        req.feedback = data.get("feedback", req.feedback)
        req.updated_at = datetime.utcnow()
        db.session.commit()
        return format_request(req)
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar solicitud: {str(e)}")

# Eliminar solicitud (soft delete) y sus relaciones
def delete_request(request_id):
    req = Request.query.filter_by(request_id=request_id, deleted_at=None).first()
    if not req:
        return False
    try:
        # Marcar cartas de liberación asociadas
        for rl in req.release_letter:
            if rl.deleted_at is None:
                rl.deleted_at = datetime.utcnow()
        # Marcar reportes asociados
        for rep in req.report:
            if rep.deleted_at is None:
                rep.deleted_at = datetime.utcnow()
        # Marcar la solicitud
        req.deleted_at = datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al eliminar solicitud y sus dependencias: {str(e)}")
