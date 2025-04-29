from app.models.user.user import User
from app.models.user.admin import Admin
from app.extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy import or_
#Función para obtener todos los administradores
def get_all_admins():
    admins = Admin.query.filter(Admin.deleted_at == None).all()
    return [format_admin(a) for a in admins]

# Función para obtener administradores paginados
def get_admins_paginated(page=1, limit=10, search_query= None):
    try:
        query = Admin.query.join(User).filter(Admin.deleted_at == None)
        
        if search_query:
            query = query.filter(
                or_(
                    User.name.ilike(f"%{search_query}%"),
                    User.institutional_email.ilike(f"%{search_query}%")
                )
            )

        total = query.count()

        admins = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "items": [format_admin(admin) for admin in admins],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit 
        }
    except Exception as e:
        raise Exception(f"Error al obtener admins paginados: {str(e)}")

#Función para obtener un administrador por su id
def get_admin_by_id(user_id):
    admin = Admin.query.filter_by(user_id=user_id, deleted_at=None).first()
    return format_admin(admin) if admin else None

#Función para crear a un administardor
def create_admin(data):
    try:
        name = data["name"]
        email = data["email"]
        password = generate_password_hash(data["password"])
        position = data.get("position", "Administrador")

        # Verificar si ya existe un usuario con ese correo
        existing_user = User.query.filter_by(institutional_email=email, deleted_at=None).first()
        if existing_user:
            raise Exception("Ya existe un administrador con ese correo institucional.")

        # Crear usuario base
        user = User(
            name=name,
            institutional_email=email,
            password=password,
            user_type=0
        )
        db.session.add(user)
        db.session.flush()  # Para obtener el user_id

        # Crear registro admin
        admin = Admin(
            user_id=user.user_id,
            position=position
        )
        db.session.add(admin)
        db.session.commit()

        return format_admin(admin)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al crear admin: {str(e)}")
    

#Función para actualizar un administrador
def update_admin(user_id, data):
    user = User.query.filter_by(user_id=user_id, user_type=0, deleted_at=None).first()
    admin = Admin.query.filter_by(user_id=user_id, deleted_at=None).first()

    if not user or not admin:
        return None

    try:
        new_email = data.get("email")

        if new_email and new_email != user.institutional_email:
            # Verificar si otro usuario ya tiene ese correo
            existing_user = User.query.filter(
                User.institutional_email == new_email,
                User.user_id != user_id,
                User.deleted_at == None
            ).first()
            if existing_user:
                raise Exception("Ya existe un administrador con ese correo institucional.")

        user.name = data.get("name", user.name)
        if new_email:
            user.institutional_email = new_email
        if "password" in data:
            user.password = generate_password_hash(data["password"])
        admin.position = data.get("position", admin.position)
        user.updated_at = datetime.utcnow()
        admin.updated_at = datetime.utcnow()

        db.session.commit()
        return format_admin(admin)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar admin: {str(e)}")



#Función para eliminar un administrador
def delete_admin(user_id):
    user = User.query.filter_by(user_id=user_id, user_type=0, deleted_at=None).first()
    admin = Admin.query.filter_by(user_id=user_id, deleted_at=None).first()

    if not user or not admin:
        return False

    try:
        user.deleted_at = datetime.utcnow()
        admin.deleted_at = datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al eliminar admin: {str(e)}")


#Función
def format_admin(admin):
    if not admin:
        return None

    user = admin.user
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.institutional_email,
        "position": admin.position,
        "user_type": user.user_type
    }
