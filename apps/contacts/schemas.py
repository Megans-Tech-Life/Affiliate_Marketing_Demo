from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class POCBase(BaseModel):
    role: Optional[str] = None
    personality_type: Optional[str] = None 
    is_deleted: Optional[bool] = None

class POCCreate(POCBase):
    leads_ids: Optional[List[UUID]] = []
    products_ids: Optional[List[UUID]] = []
    opportunities_ids: Optional[List[UUID]] = []

class POCUpdate(POCBase):
    leads_ids: Optional[List[UUID]] = []
    products_ids: Optional[List[UUID]] = []
    opportunities_ids: Optional[List[UUID]] = []

class POCResponse(POCBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Relationships
    leads: Optional[List[UUID]] = []
    products: Optional[List[UUID]] = []
    opportunities: Optional[List[UUID]] = []

    class Config:
        orm_mode = True