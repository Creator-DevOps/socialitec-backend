from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Template(db.Model):
    __tablename__ = 'template'

    document_id = db.Column(db.Integer, db.ForeignKey('document.document_id'), primary_key=True)
    description = db.Column(db.String(255))
    coordinator_id = db.Column(db.Integer, db.ForeignKey('coordinator.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    coordinator = relationship("Coordinator", back_populates="template")
    document = relationship("Document", back_populates="template")

