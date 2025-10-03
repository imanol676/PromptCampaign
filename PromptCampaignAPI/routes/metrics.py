from fastapi import APIRouter, Depends,HTTPException, File, UploadFile
from io import BytesIO
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Metric, Campaign, User  
from db.db_config import get_db
from routes.auth import get_current_user
from schemas.metric_schema import MetricCreate, MetricOut
from datetime import datetime
import httpx

metric_router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)

#create a new metric
@metric_router.post("/", response_model=MetricOut)
async def create_metric(
    metric: MetricCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    new_metric = Metric(
        campaign_id=metric.campaign_id,
        impresiones=metric.impresiones,
        clics=metric.clicks,
        conversiones=metric.conversiones,
        gasto_total=metric.gasto_total,
        fecha_registro=metric.fecha_registro
    )
    
    try:
        db.add(new_metric)
        await db.commit()
        await db.refresh(new_metric)
        return new_metric
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

# Get all metrics for a specific campaign
@metric_router.get("/{campaign_id}", response_model=list[MetricOut])
async def get_metrics_by_campaign(
    campaign_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(Metric).where(
                Metric.campaign_id == campaign_id,
                Metric.campaign_id.is_not(None)
            )
        )
        metrics = result.scalars().all()
        return metrics
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {e}")
    
# Get all metrics for the authenticated user
@metric_router.get("/", response_model=list[MetricOut])
async def get_all_metrics(
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(Metric).where(
                Metric.campaign.has(Campaign.user_id == current_user.id),
                Metric.campaign.has(Campaign.user_id.is_not(None))
            )
        )
        metrics = result.scalars().all()
        return metrics
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {e}")
    
    
#delete a metric
@metric_router.delete("/{metric_id}", response_model=dict)
async def delete_metric(
    metric_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        result = await db.execute(select(Metric).where(Metric.id == metric_id))
        metric = result.scalar_one_or_none()
        
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        await db.delete(metric)
        await db.commit()
        
        return {"detail": "Metric deleted successfully"}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

# Update a metric
@metric_router.put("/{metric_id}", response_model=MetricOut)
async def update_metric(
    metric_id: int, 
    metric_data: MetricCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        result = await db.execute(select(Metric).where(Metric.id == metric_id))
        metric = result.scalar_one_or_none()
        
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        metric.campaign_id = metric_data.campaign_id
        metric.impresiones = metric_data.impresiones
        metric.clicks = metric_data.clics
        metric.conversiones = metric_data.conversiones
        metric.gasto_total = metric_data.gasto_total
        metric.fecha_registro = metric_data.fecha_registro
        
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        
        return metric
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

# Load metrics from a file

@metric_router.post("/upload-metrics", response_model=dict)
async def upload_metrics(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Formato no soportado")

    contents = await file.read()
    
    if not contents:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    
    
    try:
        df = pd.read_csv(BytesIO(contents)) if file.filename.endswith(".csv") else pd.read_excel(BytesIO(contents))
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al leer el archivo: " + str(e))

    expected_columns = {"campaign_name", "impressions", "clicks", "conversions", "total_spend"}
    
    if not expected_columns.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail="Columnas requeridas: " + ", ".join(expected_columns))

    errors = []
    
    for _, row in df.iterrows():
        result = await db.execute(select(Campaign).filter_by(nombre=row["campaign_name"]))
        campaign = result.scalar_one_or_none()
        if not campaign:
            errors.append(f"Campaña no encontrada: {row['campaign_name']}")
            continue

        try:
            metric = Metric(
                campaign_id=campaign.id,
                impresiones=int(row["impressions"]),
                clicks=int(row["clicks"]),
                conversiones=int(row["conversions"]),
                gasto_total=float(row["total_spend"]),
                fecha_registro=datetime.utcnow().date() 
            )
            db.add(metric)
        except Exception as e:
            errors.append(f"Error en fila con campaña {row['campaign_name']}: {e}")

    await db.commit()

    return {"message": "Carga finalizada", "errores": errors if errors else "Sin errores"}




#Enviar metricas a agente n8n

@metric_router.post("/analyze/{campaign_id}", response_model=dict)
async def send_metrics_to_n8n(
    campaign_id: int,
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user),
    
):

    n8n_webhook_url = "http://localhost:5678/webhook-test/4ad0510c-8e0c-4ec8-90be-f8febd2d9fdf"
    
    try:
        result = await db.execute(
            select(Metric).where(
                Metric.campaign_id == campaign_id,
                Metric.campaign_id.is_not(None)
            )
        )
        metrics = result.scalars().all()
        
        if not metrics:
            raise HTTPException(status_code=404, detail="No se encontraron métricas para la campaña especificada")
        
        # Convertir métricas a diccionarios serializables
        metrics_data = []
        for metric in metrics:
            metric_dict = MetricOut.from_orm(metric).dict()
            # Convertir fecha a string para serialización JSON
            if 'fecha_registro' in metric_dict and metric_dict['fecha_registro']:
                metric_dict['fecha_registro'] = metric_dict['fecha_registro'].isoformat()
            metrics_data.append(metric_dict)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(n8n_webhook_url, json={"metrics": metrics_data})
            response.raise_for_status()
        
        return {"message": "Métricas enviadas a n8n exitosamente", "n8n_response": response.json()}
    
    except httpx.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con n8n: {http_err}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
        
        
