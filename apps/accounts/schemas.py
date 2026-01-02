from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime, date


# Base Schema (shared)
class AccountBase(BaseModel):

    # Basic Information
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    founded_date: Optional[date] = None
    annual_revenue: Optional[str] = None

    # Contact Details
    location: Optional[str] = None
    full_address: Optional[str] = None
    email: Optional[str] = None
    phone_code: Optional[str] = None
    phone_no: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None

    # Classification
    account_type: str = Field(default="customer", description="Type of account")
    client_type: str = Field(default="direct", description="Client relationship type")
    status: str = Field(default="active", description="Current account status")
    priority: Optional[str] = None
    segment: Optional[str] = None
    territory: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None

    # Relationships
    owner_id: Optional[uuid.UUID] = None
    owner_name: Optional[str] = None
    is_subsidiary: bool = False
    parent_account_id: Optional[str] = None

    # Keep until confirmed
    created_by: Optional[str] = None
    is_child_account: bool = False

    # Metrics
    last_activity_date: Optional[datetime] = None
    total_revenue: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        from_attributes = True

# Create Schema (required fields enforced here)
class AccountCreate(BaseModel):
    company_name: str
    account_type: str = Field(default="customer")
    client_type: str = Field(default="direct")
    status: str = Field(default="active")


# Update Schema (no required fields)
class AccountUpdate(AccountBase):
    pass

# Response Schema
class AccountResponse(AccountBase):
    id: uuid.UUID
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        from_attributes = True

class AccountNameResponse(BaseModel):
    id: uuid.UUID
    company_name: str

    class Config:
        from_attributes = True