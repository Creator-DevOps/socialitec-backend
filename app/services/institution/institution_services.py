from app.models.institution.institution import Institution
from app.extensions import db
from datetime import datetime
from sqlalchemy import or_

# Formatear institución
def format_institution(institution):
    if not institution:
        return None

    return {
        "institution_id": institution.institution_id,
        "institution_name": institution.institution_name,
        "description": institution.description,
        "phone": institution.phone,
        "email": institution.email,
        "street": institution.street,
        "number": institution.number,
        "neighborhood": institution.neighborhood,
        "postal_code": institution.postal_code,
    }

# Obtener todas las instituciones
def get_all_institutions():
    institutions = Institution.query.filter(Institution.deleted_at == None).all()
    return [format_institution(i) for i in institutions]

# Obtener instituciones paginadas
def get_institutions_paginated(page=1, limit=10, search_query = None):
    try:
        query = Institution.query.filter(Institution.deleted_at == None)
        if search_query:
            query = query.filter(
                or_(
                    Institution.institution_name.ilike(f"%{search_query}%"),
                    Institution.phone.ilike(f"%{search_query}%")
                )
            )
        total = query.count()

        institutions = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "items": [format_institution(inst) for inst in institutions],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise Exception(f"Error al obtener instituciones paginadas: {str(e)}")

# Obtener institución por ID
def get_institution_by_id(institution_id):
    institution = Institution.query.filter_by(institution_id=institution_id, deleted_at=None).first()
    return format_institution(institution) if institution else None

# Crear institución
def create_institution(data):
    try:
        institution_name = data["institution_name"]
        email = data["email"]

        # Verificar duplicados
        existing_institution = Institution.query.filter_by(institution_name=institution_name, deleted_at=None).first()
        if existing_institution:
            raise Exception("Ya existe una institución con ese nombre.")

        existing_email = Institution.query.filter_by(email=email, deleted_at=None).first()
        if existing_email:
            raise Exception("Ya existe una institución con ese correo.")

        institution = Institution(
            institution_name=institution_name,
            description=data.get("description", ""),
            phone=data.get("phone", ""),
            email=email,
            street=data.get("street", ""),
            number=data.get("number", ""),
            neighborhood=data.get("neighborhood", ""),
            postal_code=data.get("postal_code", "")
        )
        db.session.add(institution)
        db.session.commit()

        return format_institution(institution)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al crear institución: {str(e)}")

# Actualizar institución
def update_institution(institution_id, data):
    institution = Institution.query.filter_by(institution_id=institution_id, deleted_at=None).first()

    if not institution:
        return None

    try:
        new_name = data.get("institution_name")
        new_email = data.get("email")

        if new_name and new_name != institution.institution_name:
            existing_institution = Institution.query.filter(
                Institution.institution_name == new_name,
                Institution.institution_id != institution_id,
                Institution.deleted_at == None
            ).first()
            if existing_institution:
                raise Exception("Ya existe una institución con ese nombre.")

        if new_email and new_email != institution.email:
            existing_email = Institution.query.filter(
                Institution.email == new_email,
                Institution.institution_id != institution_id,
                Institution.deleted_at == None
            ).first()
            if existing_email:
                raise Exception("Ya existe una institución con ese correo.")

        institution.institution_name = new_name or institution.institution_name
        institution.description = data.get("description", institution.description)
        institution.phone = data.get("phone", institution.phone)
        institution.email = new_email or institution.email
        institution.street = data.get("street", institution.street)
        institution.number = data.get("number", institution.number)
        institution.neighborhood = data.get("neighborhood", institution.neighborhood)
        institution.postal_code = data.get("postal_code", institution.postal_code)

        institution.updated_at = datetime.utcnow()

        db.session.commit()
        return format_institution(institution)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar institución: {str(e)}")

# Eliminar institución
def delete_institution(institution_id):
    inst = Institution.query.filter_by(
        institution_id=institution_id,
        deleted_at=None
    ).first()

    if not inst:
        return False

    try:
        #programas hijos de la institución
        for prog in inst.program:   
            if prog.deleted_at is None:
                prog.deleted_at = datetime.utcnow()

        # 2) institución
        inst.deleted_at = datetime.utcnow()

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al eliminar institución y sus programas: {str(e)}")
    
# def delete_institution(institution_id):
#     institution = Institution.query.filter_by(institution_id=institution_id, deleted_at=None).first()
#     if not institution:
#         return False

#     try:
#         institution.deleted_at = datetime.utcnow()
#         db.session.commit()
#         return True
#     except Exception as e:
#         db.session.rollback()
#         raise Exception(f"Error al eliminar institución: {str(e)}")
