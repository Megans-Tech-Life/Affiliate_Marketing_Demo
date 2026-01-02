from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID as UUID_Type

class FollowUpBase(BaseModel):
    due_date: datetime = Field(..., description="When the follow-up is due")
    status: str = Field(..., description="Status of the follow-up (ex: pending, completed)")
    type: str = Field(..., description="Type of follow-up (ex:call, email)")
    notes: Optional[str] = Field(None, description="Additional notes for the follow-up")

    lead_id: Optional[UUID_Type] = None
    opportunity_id: Optional[UUID_Type] = None
    poc_id: UUID_Type
    interaction_id: UUID_Type
    assigned_user_ids: List[UUID_Type] = Field(..., min_items=1)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Follow-up type cannot be empty")
        return v.strip()
    
class FollowUpCreate(FollowUpBase):
    pass

class FollowUpUpdate(BaseModel):
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(default=None, description="Allowed values: pending, completed")
    type: Optional[str] = Field(default=None, description="Allowed values: call, email, meeting, etc.")
    notes: Optional[str] = Field(default=None, description="Notes for additional follow-up context")
    assigned_user_ids: Optional[List[UUID_Type]] = Field(default=None, min_items=1)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if not v in (None,"pending", "completed"):
            raise ValueError("Invalid status value")
        return v
    
class FollowUpResponse(BaseModel):
        id: UUID_Type
        due_date: datetime
        status: str
        type: str
        notes: Optional[str] = None

        lead_id: Optional[UUID_Type] = None
        opportunity_id: Optional[UUID_Type] = None
        poc_id: UUID_Type
        interaction_id: UUID_Type
        assigned_user_ids: List[UUID_Type]

        is_deleted: bool
        is_past_due: bool

        created_at: datetime
        updated_at: datetime
        completed_at: Optional[datetime] = None

        class Config:
            orm_mode = True