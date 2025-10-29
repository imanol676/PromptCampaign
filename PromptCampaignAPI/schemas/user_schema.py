from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    company_name: Optional[str] = None

class UserCreate(UserBase):
    hashed_password: str
    company_name: Optional[str] = None
    
class UserOut(UserBase):
    id: int
    email: EmailStr
    username: str
    company_name: Optional[str] = None

    class Config:
        from_attributes = True
