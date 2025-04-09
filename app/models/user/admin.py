from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

# Modelo Administrador
class Admin(db.Model):
    __tablename__= "admin"

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    position = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    #Relaciones
    user = relationship('User', back_populates='admin')
