from logging import info
from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime

class LeadDetailsBase(BaseModel):
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    children: Optional[int] = None
    occupation: Optional[str] = None
    job_title: Optional[str] = None
    legal_details: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    full_address: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LeadCreate(BaseModel):
    title: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_code: Optional[str] = None
    phone_no: Optional[str] = None
    entry_point: Optional[str] = None
    source: Optional[str] = None
    products: Optional[List[str]] = None
    priority: Optional[str] = None
    lead_stage: Optional[str] = None
    lead_substage: Optional[str] = None

    # Account-related info 
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None

    account_ids: Optional[List[uuid.UUID]] = None

    # LeadDetails fields
    details: Optional[LeadDetailsBase] = None

    @model_validator(mode="after")
    def validate_contact_info(self):
        has_email = bool(self.email)
        has_phone = bool(self.phone_code and self.phone_no)
        if not (has_email or has_phone):
           raise ValueError("Either email or complete phone number must be provided.")
        return self

class LeadResponse(BaseModel):
    id: uuid.UUID
    title: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone_code: Optional[str]
    phone_no: Optional[str]
    entry_point: Optional[str]
    source: Optional[str]
    priority: Optional[str]
    lead_stage: Optional[str]
    lead_substage: Optional[str]
    score: Optional[int] = None

    # Account-related info
    account_ids: List[uuid.UUID] = []
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None

    status: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_contact: Optional[bool] = None
    last_contact_at: Optional[datetime] = None
    
    # relationships
    details: Optional[LeadDetailsBase]
    products: List[str] = []

    # Convert LeadProduct ORM objects to list of product names
    @field_validator("products", mode="before")
    @classmethod
    def serialize_products(cls, value):
        if not value:
            return []
        # Extract string product names from LeadProduct objects
        return [p.product for p in value]

    model_config = ConfigDict(from_attributes=True)

class LeadValidationRequest(BaseModel):
    poc_id: Optional[uuid.UUID] = None
    account_email: Optional[str] = None
    account_phone_no: Optional[str] = None
    account_phone_code: Optional[str] = None

class LeadConvertResponse(BaseModel):
    message: str
    lead: LeadResponse

    class Config:
        from_attributes = True

class LeadUpdate(BaseModel):
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_code: Optional[str] = None
    phone_no: Optional[str] = None
    entry_point: Optional[str] = None
    source: Optional[str] = None
    products: Optional[List[str]] = None
    priority: Optional[str] = None
    
    status: Optional[str] = None
    lead_stage: Optional[str] = None
    lead_substage: Optional[str] = None

    # Account-related info 
    company: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None

    # LeadDetails fields
    details: Optional[LeadDetailsBase] = None

# Contact-focused schemas (since leads serve as contacts)
class ContactBase(BaseModel):
    title: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_code: Optional[str] = None
    phone_no: Optional[str] = None

class ContactResponse(BaseModel):
    id: uuid.UUID
    title: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone_code: Optional[str]
    phone_no: Optional[str]
    created_at: datetime
    is_contact: Optional[bool] = None

    class Config:
        from_attributes = True