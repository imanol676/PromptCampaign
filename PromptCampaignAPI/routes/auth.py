from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from routes.users import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.db_config import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt,JWTError
from models import User, Campaign, Metric  # Importar todos los modelos
from schemas.user_schema import UserOut
from utils.hash_pasword import verify_password, hash_password


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

load_dotenv()

secret_key = os.getenv("JWT_SECRET")
algorithm = os.getenv("JWT_ALGORITHM")
expire_delta = int(os.getenv("EXPIRE_MINUTES"))

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str
    

# Create User
@auth_router.post("/auth/signup", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_pwd = hash_password(user.hashed_password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pwd,
        company_name=user.company_name
    )
    
    existing_user = await db.execute(select(User).filter(User.email == user.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")
 

# Authenticate User    
async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(get_db)) -> User | None:
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# Login User
@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = jwt.encode({
        "sub": user.email, 
        "username": user.username, 
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(minutes=expire_delta)
    }, secret_key, algorithm=algorithm)
    return Token(access_token=access_token, token_type="bearer")


async def create_access_token(username:str,user_id, expires_delta: timedelta):
    to_encode = {"sub": username, "user_id": user_id}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> User:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials - user_id missing")
            
        return User(username=username, id=user_id)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")
         