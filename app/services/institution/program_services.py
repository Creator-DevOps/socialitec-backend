from app.models.institution.program import Program
from app.models.institution.institution import Institution
from app.extensions import db
from datetime import datetime
from sqlalchemy import or_

# Formatear programa
def format_program(program):
    if not program:
        return None

    return {
        "program_id": program.program_id,
        "institution_id": program.institution_id,
        "program_name": program.program_name,
        "description": program.description,
        "activities": program.activities,
        "supervisor_name": program.supervisor_name,
        "supervisor_phone": program.supervisor_phone,
        "supervisor_email": program.supervisor_email
    }

# Obtener todos los programas
def get_all_programs():
    programs = Program.query.filter(Program.deleted_at == None).all()
    return [format_program(p) for p in programs]

# Obtener programas paginados
def get_programs_paginated(page=1, limit=10, search_query = None):
    try:
        query = Program.query.join(Institution).filter(Program.deleted_at == None)
        if search_query:
            query = query.filter(
                or_(
                    Program.program_name.ilike(f"%{search_query}%"),
                    Program.supervisor_name.ilike(f"%{search_query}%")
                )
            )
        total = query.count()

        programs = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "items": [format_program(prog) for prog in programs],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise Exception(f"Error al obtener programas paginados: {str(e)}")

# Obtener programa por ID
def get_program_by_id(program_id):
    program = Program.query.filter_by(program_id=program_id, deleted_at=None).first()
    return format_program(program) if program else None

# Crear programa
def create_program(data):
    try:
        institution_id = data["institution_id"]
        program_name = data["program_name"]

        # Verificar si existe la institución
        institution = Institution.query.filter_by(institution_id=institution_id, deleted_at=None).first()
        if not institution:
            raise Exception("La institución asignada no existe.")

        # Verificar si ya existe un programa con el mismo nombre en la misma institución
        existing_program = Program.query.filter_by(
            program_name=program_name,
            institution_id=institution_id,
            deleted_at=None
        ).first()
        if existing_program:
            raise Exception("Ya existe un programa con ese nombre en esta institución.")

        program = Program(
            institution_id=institution_id,
            program_name=program_name,
            description=data.get("description", ""),
            activities=data.get("activities", ""),
            supervisor_name=data.get("supervisor_name", ""),
            supervisor_phone=data.get("supervisor_phone", ""),
            supervisor_email=data.get("supervisor_email", "")
        )
        db.session.add(program)
        db.session.commit()

        return format_program(program)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al crear programa: {str(e)}")

# Actualizar programa
def update_program(program_id, data):
    program = Program.query.filter_by(program_id=program_id, deleted_at=None).first()

    if not program:
        return None

    try:
        new_program_name = data.get("program_name")
        new_institution_id = data.get("institution_id", program.institution_id)

        # Verificar si se cambia la institución
        if new_institution_id != program.institution_id:
            institution = Institution.query.filter_by(institution_id=new_institution_id, deleted_at=None).first()
            if not institution:
                raise Exception("La institución asignada no existe.")

        # Verificar si cambia nombre y/o institución
        if (new_program_name and new_program_name != program.program_name) or (new_institution_id != program.institution_id):
            existing_program = Program.query.filter(
                Program.program_name == (new_program_name or program.program_name),
                Program.institution_id == new_institution_id,
                Program.program_id != program_id,
                Program.deleted_at == None
            ).first()
            if existing_program:
                raise Exception("Ya existe un programa con ese nombre en esta institución.")

        program.institution_id = new_institution_id
        program.program_name = new_program_name or program.program_name
        program.description = data.get("description", program.description)
        program.activities = data.get("activities", program.activities)
        program.supervisor_name = data.get("supervisor_name", program.supervisor_name)
        program.supervisor_phone = data.get("supervisor_phone", program.supervisor_phone)
        program.supervisor_email = data.get("supervisor_email", program.supervisor_email)

        program.updated_at = datetime.utcnow()

        db.session.commit()
        return format_program(program)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar programa: {str(e)}")

# Eliminar programa
def delete_program(program_id):
    program = Program.query.filter_by(program_id=program_id, deleted_at=None).first()

    if not program:
        return False

    try:
        program.deleted_at = datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al eliminar programa: {str(e)}")
