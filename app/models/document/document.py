from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'document'

    document_id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.SmallInteger)  # 0 = report, 1 = template, 2 = release_letter
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    template = relationship("Template", back_populates="document", uselist=False)
    report = relationship("Report", back_populates="document", uselist=False)
    release_letter = relationship("ReleaseLetter", back_populates="document", uselist=False)
