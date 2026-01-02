from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    first_name: str
    last_name: str
    phone_code: Optional[str] = None
    phone_no: Optional[str] = None
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CheckEmailRequest(BaseModel):
    email: EmailStr

class CheckEmailResponse(BaseModel):
    exists: bool

class UserResponse(UserBase):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserOut(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    phone_code: Optional[str] = None
    phone_no: Optional[str] = None
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: Optional[int] = None