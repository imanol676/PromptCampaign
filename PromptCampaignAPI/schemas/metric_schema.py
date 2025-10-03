from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class MetricBase(BaseModel):
    campaign_id: int
    impresiones: int
    clicks: int
    conversiones: int
    gasto_total: float
    fecha_registro: date
    
class MetricCreate(MetricBase):
    pass

class MetricOut(MetricBase):
    id: int

    class Config:
        from_attributes = True  