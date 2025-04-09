from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Program(db.Model):
    __tablename__ = 'program'

    program_id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.institution_id'))
    program_name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    activities = db.Column(db.String(255))
    supervisor_name = db.Column(db.String(100))
    supervisor_phone = db.Column(db.String(20))
    supervisor_email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    request = relationship("Request", back_populates="program")
    institution = relationship("Institution", back_populates="program")
