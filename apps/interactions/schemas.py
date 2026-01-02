from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class InteractionType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MESSAGE = "MESSAGE"
    MEETING = "MEETING"
    FOLLOW_UP = "FOLLOW_UP"
    DEMO = "DEMO"
    NOTE = "NOTE"
    OTHER = "OTHER"

class InteractionBase(BaseModel):
    type: InteractionType
    occurred_at: Optional[datetime] = None
    subject: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    next_steps: Optional[str] = None
    account_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    person_id: Optional[UUID] = None

class InteractionCreate(InteractionBase):
      pass

class InteractionResponse(InteractionBase):
    id: UUID
    occurred_at: datetime
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class InteractionUpdate(BaseModel):
    subject: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    next_steps: Optional[str] = None
    occurred_at: Optional[datetime] = None
