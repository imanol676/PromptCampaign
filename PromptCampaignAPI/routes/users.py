from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.future import select  
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserCreate, UserOut
from models import User, Campaign, Metric  # Importar todos los modelos
from db.db_config import get_db
from utils.hash_pasword import hash_password
from routes.auth import get_current_user


user_router = APIRouter(
    prefix="/users",
    tags=["users"]
)


#Get User
@user_router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
   try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
   except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {e}")

    
    
#Get All Users
@user_router.get("/users/", response_model=list[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_db)):
   try:
       result = await db.execute(select(User))
       users = result.scalars().all()
       return users
   
   except Exception as e:
       await db.rollback()
       raise HTTPException(status_code=500, detail=f"Error retrieving users: {e}")
   
# Delete User
@user_router.delete("/users/{user_id}", response_model=UserOut)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await db.delete(user)
        await db.commit()
        return user

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")
    
# Update User
@user_router.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.email = user_data.email
        user.username = user_data.username
        user.company_name = user_data.company_name
        if user_data.hashed_password:
            user.hashed_password = hash_password(user_data.hashed_password)

        await db.commit()
        await db.refresh(user)
        return user

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")


