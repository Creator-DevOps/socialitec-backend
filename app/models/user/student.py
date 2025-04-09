from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'student'

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    control_number = db.Column(db.String(50), nullable=False, unique=True)
    major = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    credits = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relaciones
    user = relationship('User', back_populates='student')
    report = relationship('Report', back_populates='student')
    request = relationship('Request', back_populates='student')