from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'request'

    request_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.user_id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.program_id'), nullable=False)
    acceptance_status = db.Column(db.SmallInteger)
    progress_status = db.Column(db.SmallInteger)
    request_date = db.Column(db.Date)
    completed_hours = db.Column(db.Integer, default=0)
    coordinator_id = db.Column(db.Integer, db.ForeignKey('coordinator.user_id'))
    feedback = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    #Relaciones
    student = relationship("Student", back_populates="request")
    program = relationship("Program", back_populates="request")
    coordinator = relationship("Coordinator", back_populates="request")
    release_letter = relationship("ReleaseLetter", back_populates="request")
    report = relationship("Report", back_populates="request")

