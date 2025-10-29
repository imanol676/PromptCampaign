from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .user import base

class Metric(base):
    __tablename__ = "Metric"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("Campaign.id"), nullable=False)
    impresiones = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    conversiones = Column(Integer, nullable=False)
    gasto_total = Column(DECIMAL, nullable=False)
    fecha_registro = Column(Date, nullable=False)

    campaign = relationship("Campaign", back_populates="metrics")
    feedbacks = relationship("Feedback", back_populates="metric", cascade="all, delete-orphan")
