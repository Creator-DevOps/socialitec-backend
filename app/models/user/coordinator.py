from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Coordinator(db.Model):
    __tablename__ = 'coordinator'

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    departament = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    #Relaciones
    user = relationship('User', back_populates='coordinator')
    template = relationship('Template', back_populates='coordinator')
    report = relationship('Report', back_populates='coordinator')
    release_letter = relationship('ReleaseLetter', back_populates='coordinator')
    request = relationship("Request", back_populates="coordinator")

