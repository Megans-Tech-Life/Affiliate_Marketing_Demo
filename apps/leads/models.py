import uuid
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Table, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from apps.followups.models import FollowUp
from core.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from apps.followups.models import FollowUp

# Many-to-Many relationship between Leads and Accounts
lead_accounts = Table(
    "lead_accounts",
    Base.metadata,
    Column("lead_id", UUID(as_uuid=True), ForeignKey("leads.id")),
    Column("account_id", UUID(as_uuid=True), ForeignKey("accounts.id"))
)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), nullable=True)
    phone_code = Column(String(10), nullable=True)
    phone_no = Column(String(50), nullable=True)
    
    # Account related info captured at lead creation
    company_name = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    entry_point = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    priority = Column(String(50), nullable=True)

    lead_stage = Column(String, nullable=True)  
    lead_substage = Column(String, nullable=True)
    score = Column(Integer, nullable=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=True) 

    is_contact = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_contact_at = Column(DateTime(timezone=True), nullable=True)

    # Status of the lead in the sales funnel
    status = Column(String(50), default="New") #(New, Contacted, Qualified, etc.)

    # User who owns the lead
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    affiliate_link_id = Column(UUID(as_uuid=True), ForeignKey("affiliate_links.id"), nullable=True, index=True)

    # Relationships
    accounts = relationship("Account", secondary="lead_accounts", back_populates="contacts", lazy="joined")
    persons = relationship("PersonOfContact", secondary="person_leads", back_populates="leads", lazy="joined")
    details = relationship("LeadDetails", uselist=False, back_populates="lead", lazy="joined")
    notes = relationship("LeadNote", back_populates="lead", lazy="joined")
    products = relationship("LeadProduct", back_populates="lead", lazy="joined")
    opportunities = relationship("Opportunity", secondary="opportunity_leads", back_populates="leads", lazy="joined")
    user = relationship("User", back_populates="leads", overlaps="owner", lazy="joined")
    owner = relationship("User", back_populates="leads")
    affiliate_link = relationship("AffiliateLink", back_populates="leads", lazy="joined")
    interactions = relationship("Interaction", back_populates="lead", lazy="joined")
    followups = relationship("FollowUp", back_populates="lead", lazy="joined")

class LeadDetails(Base):
    __tablename__ = "lead_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"))
    dob = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    marital_status = Column(String(50), nullable=True)
    children = Column(Integer, nullable=True)
    occupation = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    legal_details = Column(String(50), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    twitter_url = Column(String(255), nullable=True)
    instagram_url = Column(String(255), nullable=True)
    full_address = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)

    lead = relationship("Lead", back_populates="details", lazy="joined")

class LeadNote(Base):
    __tablename__ = "lead_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"))
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # affiliate_user_id
    lead = relationship("Lead", back_populates="notes")

class LeadProduct(Base):
    __tablename__ = "lead_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"))
    product = Column(String(255), nullable=False)   
    interest_level = Column(String(50), nullable=True)

    # Relationship 
    lead = relationship("Lead", back_populates="products")
