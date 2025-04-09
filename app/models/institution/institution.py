from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Institution(db.Model):
    __tablename__ = 'institution'

    institution_id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    street = db.Column(db.String(100))
    number = db.Column(db.String(10))
    neighborhood = db.Column(db.String(100))
    postal_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    program = relationship("Program", back_populates="institution")
