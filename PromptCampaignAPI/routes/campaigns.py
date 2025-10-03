from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Campaign, User, Metric  # Importar todos los modelos
from schemas.campaign_schema import CampaignCreate, CampaignOut
from db.db_config import get_db
from routes.auth import get_current_user

campaign_router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"],
)

# Create a new campaign
@campaign_router.post("/", response_model=CampaignOut)
async def create_campaign(
    campaign: CampaignCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    new_campaign = Campaign(
        nombre=campaign.nombre,
        plataforma=campaign.plataforma,
        fecha_inicio=campaign.fecha_inicio,
        fecha_fin=campaign.fecha_fin,
        presupuesto=campaign.presupuesto,
        user_id=current_user.id  
    )
    
    try:
    
        db.add(new_campaign)
        await db.commit()
        await db.refresh(new_campaign)
        return new_campaign
    
    except Exception as e:
        
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    
# Get all campaigns
@campaign_router.get("/", response_model=list[CampaignOut])
async def get_campaigns(
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
  try:  
       # Filtrar solo las campañas del usuario autenticado y que tengan user_id válido
       result = await db.execute(
           select(Campaign).where(
               Campaign.user_id == current_user.id,
               Campaign.user_id.is_not(None)
           )
       )
       campaigns = result.scalars().all()
       return campaigns
    
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=400, detail=str(e))


# Get a campaign by ID
@campaign_router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
  try:  
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == current_user.id))
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))


#delete a campaign
@campaign_router.delete("/{campaign_id}", response_model=dict)
async def delete_campaign(
    campaign_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == current_user.id))
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        await db.delete(campaign)
        await db.commit()
        
        return {"detail": "Campaign deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Update a campaign
@campaign_router.put("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: int, 
    campaign: CampaignCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == current_user.id))
        existing_campaign = result.scalar_one_or_none()
        
        if not existing_campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        for key, value in campaign.dict().items():
            setattr(existing_campaign, key, value)
        
        await db.commit()
        await db.refresh(existing_campaign)
        
        return existing_campaign
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))