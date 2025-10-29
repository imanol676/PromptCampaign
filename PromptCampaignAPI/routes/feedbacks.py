from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.feedback import Feedback
from models.campaign import Campaign
from models.metric import Metric
from schemas.n8n_schema import (
    SendMetricsToN8nRequest,
    MetricDataForAI,
    ReceiveFeedbackFromN8n,
    SendMetricsResponse
)
from schemas.feedback_schema import FeedbackOut
from db.db_config import get_db
import httpx
from typing import List
from datetime import datetime

Feedback_router = APIRouter(
    prefix="/feedbacks",
    tags=["Feedbacks"],
)


# Endpoint para enviar métricas de una campaña al workflow de n8n
@Feedback_router.post("/send-to-n8n", response_model=SendMetricsResponse)
async def send_metrics_to_n8n(
    request: SendMetricsToN8nRequest,
    db: AsyncSession = Depends(get_db)
):
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == request.campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaña con id {request.campaign_id} no encontrada"
        )
    
    if request.metric_id:
        metric_result = await db.execute(
            select(Metric).where(
                Metric.id == request.metric_id,
                Metric.campaign_id == request.campaign_id
            )
        )
        metric = metric_result.scalar_one_or_none()
        
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Métrica con id {request.metric_id} no encontrada"
            )
    else:
        metric_result = await db.execute(
            select(Metric)
            .where(Metric.campaign_id == request.campaign_id)
            .order_by(Metric.fecha_registro.desc())
        )
        metric = metric_result.scalar_one_or_none()
        
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron métricas para la campaña"
            )
    
    ctr = (metric.clicks / metric.impresiones * 100) if metric.impresiones > 0 else 0
    conversion_rate = (metric.conversiones / metric.clicks * 100) if metric.clicks > 0 else 0
    cpc = (float(metric.gasto_total) / metric.clicks) if metric.clicks > 0 else 0
    cpa = (float(metric.gasto_total) / metric.conversiones) if metric.conversiones > 0 else 0
    
    metric_data = MetricDataForAI(
        campaign_id=campaign.id,
        campaign_nombre=campaign.nombre,
        campaign_plataforma=campaign.plataforma,
        metric_id=metric.id,
        impresiones=metric.impresiones,
        clicks=metric.clicks,
        conversiones=metric.conversiones,
        gasto_total=float(metric.gasto_total),
        fecha_registro=metric.fecha_registro,
        ctr=round(ctr, 2),
        conversion_rate=round(conversion_rate, 2),
        cpc=round(cpc, 2),
        cpa=round(cpa, 2)
    )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                str(request.n8n_webhook_url),
                json=metric_data.model_dump(mode='json')
            )
            response.raise_for_status()
            
            return SendMetricsResponse(
                success=True,
                message="Métricas enviadas exitosamente a n8n",
                campaign_id=campaign.id,
                metric_id=metric.id,
                n8n_response_status=response.status_code
            )
            
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al comunicarse con n8n: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )


@Feedback_router.post("/receive-from-n8n", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def receive_feedback_from_n8n(
    feedback_data: ReceiveFeedbackFromN8n,
    db: AsyncSession = Depends(get_db)
):
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == feedback_data.campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaña con id {feedback_data.campaign_id} no encontrada"
        )
    
    metric_result = await db.execute(
        select(Metric).where(
            Metric.id == feedback_data.metric_id,
            Metric.campaign_id == feedback_data.campaign_id
        )
    )
    metric = metric_result.scalar_one_or_none()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Métrica con id {feedback_data.metric_id} no encontrada"
        )
    
    new_feedback = Feedback(
        campaign_id=feedback_data.campaign_id,
        metric_id=feedback_data.metric_id,
        texto_feedback=feedback_data.texto_feedback
    )
    
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    
    return new_feedback


@Feedback_router.get("/campaign/{campaign_id}", response_model=List[FeedbackOut])
async def get_feedbacks_by_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaña con id {campaign_id} no encontrada"
        )
    
    feedbacks_result = await db.execute(
        select(Feedback).where(Feedback.campaign_id == campaign_id)
    )
    feedbacks = feedbacks_result.scalars().all()
    
    return feedbacks


@Feedback_router.get("/{feedback_id}", response_model=FeedbackOut)
async def get_feedback_by_id(
    feedback_id: int,
    db: AsyncSession = Depends(get_db)
):
    feedback_result = await db.execute(
        select(Feedback).where(Feedback.id == feedback_id)
    )
    feedback = feedback_result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback con id {feedback_id} no encontrado"
        )
    
    return feedback


@Feedback_router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db)
):
    feedback_result = await db.execute(
        select(Feedback).where(Feedback.id == feedback_id)
    )
    feedback = feedback_result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback con id {feedback_id} no encontrado"
        )
    
    await db.delete(feedback)
    await db.commit()
    
    return None
