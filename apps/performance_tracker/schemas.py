from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PerformanceBase(BaseModel):
    salesperson_id: UUID
    total_leads: int
    total_opportunities: int
    closed_deals: int
    conversion_rate: float
    total_commission: float

class PerformanceResponse(PerformanceBase):
    id: UUID
    recorded_at: datetime
    class Config:
        orm_mode = True
