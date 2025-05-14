from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class ReportCycleItem(db.Model):
    __tablename__ = "report_cycle_item"

    item_id       = db.Column(db.Integer, primary_key=True)
    cycle_id      = db.Column(db.Integer,
                              db.ForeignKey("report_cycle.cycle_id"),
                              nullable=False)
    report_number = db.Column(db.SmallInteger, nullable=False)
    title         = db.Column(db.String(100), nullable=False)
    start_date    = db.Column(db.Date, nullable=False)
    end_date      = db.Column(db.Date, nullable=False)

    cycle         = relationship("ReportCycle", back_populates="items")
    submissions   = relationship("Report", back_populates="cycle_item")
