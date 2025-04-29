from app.models.user.user import User
from app.extensions import db
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

def login_service(email, password):
    user = User.query.filter_by(institutional_email=email, deleted_at=None).first()

    if not user:
        raise Exception("Usuario no encontrado o eliminado.")

    if not check_password_hash(user.password, password):
        raise Exception("Contraseña incorrecta.")

    # Crear token válido por 1 día
    token = create_access_token(identity=str(user.user_id), expires_delta=timedelta(days=1))

    # Armar respuesta
    user_info = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.institutional_email,
        "user_type": user.user_type
    }

    # Especialización
    if user.user_type == 0 and user.admin:
        user_info["position"] = user.admin.position
    elif user.user_type == 1 and user.coordinator:
        user_info["departament"] = user.coordinator.departament
    elif user.user_type == 2 and user.student:
        user_info["control_number"] = user.student.control_number
        user_info["major"] = user.student.major
        user_info["semester"] = user.student.semester
        user_info["credits"] = user.student.credits

    return {
        "token": token,
        "user": user_info
    }


