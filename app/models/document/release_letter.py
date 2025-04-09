from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class ReleaseLetter(db.Model):
    __tablename__ = 'release_letter'

    document_id = db.Column(db.Integer, db.ForeignKey('document.document_id'), primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('request.request_id'))
    coordinator_id = db.Column(db.Integer, db.ForeignKey('coordinator.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    #Relaciones
    coordinator = relationship("Coordinator", back_populates="release_letter")
    document = relationship("Document", back_populates="release_letter")
    request = relationship("Request", back_populates="release_letter")
