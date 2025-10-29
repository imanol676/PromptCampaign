from fastapi import FastAPI
from routes.users import user_router
from routes.auth import auth_router
from routes.auth import get_current_user
from routes.metrics import metric_router
from routes.campaigns import campaign_router
from routes.feedbacks import Feedback_router
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

# Importar todos los modelos para que SQLAlchemy los configure correctamente
from models import User, Campaign, Metric, Feedback, base

from schemas.user_schema import UserOut


oaut_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


app = FastAPI(
    title="PromptCampaign",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    return "Welcome to PromptCampaign API!"


# Include the user router
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(campaign_router)
app.include_router(metric_router)
app.include_router(Feedback_router)





