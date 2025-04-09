from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'report'

    document_id = db.Column(db.Integer, db.ForeignKey('document.document_id'), primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('request.request_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.user_id'))
    coordinator_id = db.Column(db.Integer, db.ForeignKey('coordinator.user_id'))
    report_number = db.Column(db.SmallInteger, nullable=False)
    status = db.Column(db.SmallInteger, default=0)
    feedback = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    #Relaciones
    coordinator = relationship("Coordinator", back_populates="report")
    document = relationship("Document", back_populates="report")
    request = relationship("Request", back_populates="report")
    student = relationship("Student", back_populates="report")
