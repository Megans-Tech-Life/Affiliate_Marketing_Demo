from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class OpportunityBase(BaseModel):
    name: str
    description: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    price_value: Optional[dict] = None  # Example {"base_price": 1000.0, "estimated_price": 1200.0}

class OpportunityCreate(OpportunityBase):
    leads_ids: Optional[List[UUID]] = []
    poc_ids: Optional[List[UUID]] = []
    products_ids: Optional[List[UUID]] = []

class OpportunityUpdate(OpportunityBase):
    leads_ids: Optional[List[UUID]] = []
    poc_ids: Optional[List[UUID]] = []
    products_ids: Optional[List[UUID]] = []

class OpportunityResponse(OpportunityBase):
    id: UUID

    class Config:
        from_attributes = True
