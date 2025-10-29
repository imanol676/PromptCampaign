from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .user import base


class Campaign(base):
    __tablename__ = "Campaign"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    plataforma = Column(String, nullable=False)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    presupuesto = Column(DECIMAL)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)

    user = relationship("User", back_populates="campaigns")
    metrics = relationship("Metric", back_populates="campaign", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="campaign", cascade="all, delete-orphan")

