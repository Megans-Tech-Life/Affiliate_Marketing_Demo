from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class CommissionStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    canceled = "canceled"

class CommissionBase(BaseModel):
    salesperson_id: UUID
    opportunity_id: Optional[UUID]
    amount: float
    percentage: Optional[float] = None
    status: Optional[CommissionStatus] = CommissionStatus.pending
    payment_date: Optional[datetime] = None

class CommissionCreate(CommissionBase):
    pass

class CommissionUpdate(BaseModel):
    status: Optional[CommissionStatus]
    payment_date: Optional[datetime]

class CommissionResponse(CommissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True