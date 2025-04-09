from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

# Modelo Usuario
class User (db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    institutional_email = db.Column(db.String(100), nullable = False, unique= True)
    password = db.Column(db.String(255), nullable = False)
    user_type = db.Column(db.SmallInteger, nullable = False) # 0: Admin, 1: Coordinator, 2: Student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable = True)

    # Relaciones
    admin = relationship('Admin', back_populates='user', uselist=False)
    coordinator = relationship('Coordinator', back_populates='user', uselist=False)
    student = relationship('Student', back_populates='user', uselist=False)

