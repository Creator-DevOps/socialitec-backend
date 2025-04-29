from app.models.user.user import User
from app.models.user.coordinator import Coordinator
from app.extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy import or_

# Formatear coordinator
def format_coordinator(coordinator):
    if not coordinator:
        return None

    user = coordinator.user
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.institutional_email,
        "departament": coordinator.departament,
        "user_type": user.user_type
    }

# Obtener todos los coordinadores
def get_all_coordinators():
    coordinators = Coordinator.query.filter(Coordinator.deleted_at == None).all()
    return [format_coordinator(c) for c in coordinators]

# Obtener coordinadores paginados
def get_coordinators_paginated(page=1, limit=10, search_query=None):
    try:
        query = Coordinator.query.join(User).filter(Coordinator.deleted_at == None)

        if search_query:
            query = query.filter(
                or_(
                    User.name.ilike(f"%{search_query}%"),
                    User.institutional_email.ilike(f"%{search_query}%")
                )
            )

        total = query.count()
        coordinators = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "items": [format_coordinator(coordinator) for coordinator in coordinators],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise Exception(f"Error al obtener coordinadores paginados: {str(e)}")


# Obtener coordinator por ID
def get_coordinator_by_id(user_id):
    coordinator = Coordinator.query.filter_by(user_id=user_id, deleted_at=None).first()
    return format_coordinator(coordinator) if coordinator else None

# Crear coordinator
def create_coordinator(data):
    try:
        name = data["name"]
        email = data["email"]
        password = generate_password_hash(data["password"])
        departament = data.get("departament", "")

        # Verificar si ya existe el correo
        existing_user = User.query.filter_by(institutional_email=email, deleted_at=None).first()
        if existing_user:
            raise Exception("Ya existe un coordinador con ese correo institucional.")

        # Crear usuario base
        user = User(
            name=name,
            institutional_email=email,
            password=password,
            user_type=1  # Suponiendo tipo 1 = coordinador
        )
        db.session.add(user)
        db.session.flush()

        # Crear registro coordinator
        coordinator = Coordinator(
            user_id=user.user_id,
            departament=departament
        )
        db.session.add(coordinator)
        db.session.commit()

        return format_coordinator(coordinator)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al crear coordinador: {str(e)}")

# Actualizar coordinator
def update_coordinator(user_id, data):
    user = User.query.filter_by(user_id=user_id, user_type=1, deleted_at=None).first()
    coordinator = Coordinator.query.filter_by(user_id=user_id, deleted_at=None).first()

    if not user or not coordinator:
        return None

    try:
        new_email = data.get("email")

        if new_email and new_email != user.institutional_email:
            existing_user = User.query.filter(
                User.institutional_email == new_email,
                User.user_id != user_id,
                User.deleted_at == None
            ).first()
            if existing_user:
                raise Exception("Ya existe un coordinador con ese correo institucional.")

        user.name = data.get("name", user.name)
        if new_email:
            user.institutional_email = new_email
        if "password" in data:
            user.password = generate_password_hash(data["password"])
        coordinator.departament = data.get("departament", coordinator.departament)

        user.updated_at = datetime.utcnow()
        coordinator.updated_at = datetime.utcnow()

        db.session.commit()
        return format_coordinator(coordinator)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar coordinador: {str(e)}")

# Eliminar coordinator
def delete_coordinator(user_id):
    user = User.query.filter_by(user_id=user_id, user_type=1, deleted_at=None).first()
    coordinator = Coordinator.query.filter_by(user_id=user_id, deleted_at=None).first()

    if not user or not coordinator:
        return False

    try:
        user.deleted_at = datetime.utcnow()
        coordinator.deleted_at = datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al eliminar coordinador: {str(e)}")
