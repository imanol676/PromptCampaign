from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .user import base

class Feedback(base):
    __tablename__ = "Feedback"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("Campaign.id"), nullable=False)
    metric_id = Column(Integer, ForeignKey("Metric.id"), nullable=False)
    texto_feedback = Column(Text, nullable=False)
    
    campaign = relationship("Campaign", back_populates="feedbacks")
    metric = relationship("Metric", back_populates="feedbacks")