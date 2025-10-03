from datetime import date
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import field_validator

class CampaignBase(BaseModel):
    nombre: str
    plataforma: str
    fecha_inicio: date           
    fecha_fin: Optional[date]     
    presupuesto: Optional[float]
    
    @field_validator('fecha_inicio', 'fecha_fin', mode='before')
    def parse_date(cls, value):
        if isinstance(value, str):
            try:
                # Proba primero formato ISO
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                # Si falla, probá con el formato que te manda el frontend
                return datetime.strptime(value, "%d/%m/%Y").date()
        return value
    
class CampaignCreate(CampaignBase):
    pass

class CampaignOut(CampaignBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
