from datetime import datetime
import uuid
from pydantic import BaseModel, Field

class AdminLoginRequest(BaseModel):
    admin_id: str = Field(..., description="superadmin")
    password: str = Field(..., description="supersecretpassword")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Expiration time in 60 minutes")

class AdminAccountResponse(BaseModel):
        id: uuid.UUID
        company_name: str
        owner_id: uuid.UUID
        owner_name: str
        account_type: str
        client_type: str
        created_at: datetime
        is_deleted: bool

        class Config:
            from_attributes = True