from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import date

# Schema para enviar métricas a n8n
class MetricDataForAI(BaseModel):
    """Datos de métricas que se enviarán a n8n para análisis de IA"""
    campaign_id: int
    campaign_nombre: str
    campaign_plataforma: str
    metric_id: int
    impresiones: int
    clicks: int
    conversiones: int
    gasto_total: float
    fecha_registro: date
    # Métricas calculadas
    ctr: float  # Click Through Rate
    conversion_rate: float  # Tasa de conversión
    cpc: float  # Costo por click
    cpa: float  # Costo por adquisición/conversión

    class Config:
        from_attributes = True

# Schema para el request que envía métricas a n8n
class SendMetricsToN8nRequest(BaseModel):
    """Request para enviar métricas de una campaña al workflow de n8n"""
    campaign_id: int
    metric_id: Optional[int] = None  # Si no se especifica, se envía la métrica más reciente
    n8n_webhook_url: HttpUrl  # URL del webhook de n8n

# Schema para recibir el feedback desde n8n
class ReceiveFeedbackFromN8n(BaseModel):
    """Feedback generado por la IA en n8n que será guardado en la base de datos"""
    campaign_id: int
    metric_id: int
    texto_feedback: str
    
    class Config:
        from_attributes = True

# Schema de respuesta al enviar métricas
class SendMetricsResponse(BaseModel):
    """Respuesta después de enviar métricas a n8n"""
    success: bool
    message: str
    campaign_id: int
    metric_id: int
    n8n_response_status: Optional[int] = None
