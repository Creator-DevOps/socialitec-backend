from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class ReportCycle(db.Model):
    __tablename__ = "report_cycle"

    cycle_id    = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    folder_name = db.Column(db.String(100), nullable=False)
    start_date  = db.Column(db.Date, nullable=False)
    end_date    = db.Column(db.Date, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow)
    
    requests    = relationship("Request", back_populates="cycle")
    items       = relationship("ReportCycleItem", back_populates="cycle")