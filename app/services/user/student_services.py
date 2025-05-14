from app.models.user.user import User
from app.models.user.student import Student
from app.extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy import or_

# Función para dar formato a un estudiante
def format_student(student):
    if not student:
        return None

    user = student.user
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.institutional_email,
        "control_number": student.control_number,
        "major": student.major,
        "semester": student.semester,
        "credits": student.credits,
        "user_type": user.user_type
    }

# Obtener todos los estudiantes
def get_all_students():
    students = Student.query.filter(Student.deleted_at == None).all()
    return [format_student(s) for s in students]

# Obtener estudiantes paginados
def get_students_paginated(page=1, limit=10, search_query = None):
    try:
        query = Student.query.join(User).filter(Student.deleted_at == None)
        if search_query:
            query = query.filter(
                or_(
                    User.name.ilike(f"%{search_query}%"),
                    User.institutional_email.ilike(f"%{search_query}%")
                )
            )
        total = query.count()
        students = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "items": [format_student(student) for student in students],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise Exception(f"Error al obtener estudiantes paginados: {str(e)}")

# Obtener estudiante por ID
def get_student_by_id(user_id):
    student = Student.query.filter_by(user_id=user_id, deleted_at=None).first()
    return format_student(student) if student else None

# Crear un estudiante
def create_student(data):
    try:
        name = data["name"]
        email = data["email"]
        password = generate_password_hash(data["password"])
        control_number = data["control_number"]
        major = data.get("major", "")
        semester = data.get("semester", None)
        credits = data.get("credits", 0)

        # Verificar si el email o número de control ya existe
        existing_user = User.query.filter_by(institutional_email=email, deleted_at=None).first()
        if existing_user:
            raise Exception("Ya existe un usuario con ese correo institucional.")

        existing_control = Student.query.filter_by(control_number=control_number, deleted_at=None).first()
        if existing_control:
            raise Exception("Ya existe un estudiante con ese número de control.")

        # Crear usuario base
        user = User(
            name=name,
            institutional_email=email,
            password=password,
            user_type=2 #Tipo 2 = estudiante
        )
        db.session.add(user)
        db.session.flush()

        # Crear registro estudiante
        student = Student(
            user_id=user.user_id,
            control_number=control_number,
            major=major,
            semester=semester,
            credits=credits
        )
        db.session.add(student)
        db.session.commit()

        return format_student(student)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al crear estudiante: {str(e)}")

# Actualizar un estudiante
def update_student(user_id, data):
    user = User.query.filter_by(user_id=user_id, user_type=2, deleted_at=None).first()
    student = Student.query.filter_by(user_id=user_id, deleted_at=None).first()

    if not user or not student:
        return None

    try:
        new_email = data.get("email", "").lower()
        new_control = data.get("control_number")

        if new_email and new_email != user.institutional_email.lower():
            existing_user = User.query.filter(
                User.institutional_email == new_email,
                User.user_id != user_id,
                User.deleted_at == None
            ).first()
            if existing_user:
                raise Exception("Ya existe un usuario con ese correo institucional.")

        if new_control and new_control != student.control_number:
            existing_control = Student.query.filter(
                Student.control_number == new_control,
                Student.user_id != user_id,
                Student.deleted_at == None
            ).first()
            if existing_control:
                raise Exception("Ya existe un estudiante con ese número de control.")

        user.name = data.get("name", user.name)
        if new_email:
            user.institutional_email = new_email
        if "password" in data:
            user.password = generate_password_hash(data["password"])
        student.control_number = new_control or student.control_number
        student.major = data.get("major", student.major)
        student.semester = data.get("semester", student.semester)
        student.credits = data.get("credits", student.credits)

        user.updated_at = datetime.utcnow()
        student.updated_at = datetime.utcnow()

        db.session.commit()
        return format_student(student)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar estudiante: {str(e)}")

# Eliminar un estudiante
def delete_student(user_id):
    user = User.query.filter_by(user_id=user_id, user_type=2, deleted_at=None).first()
    student = Student.query.filter_by(user_id=user_id, deleted_at=None).first()

    if not user or not student:
        return False

    try:
        user.deleted_at = datetime.utcnow()
        student.deleted_at = datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al eliminar estudiante: {str(e)}")
