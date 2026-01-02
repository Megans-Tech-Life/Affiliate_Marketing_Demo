import uuid
from sqlalchemy import Boolean, Column, String, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    # Primary
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    shop_domain = Column(String(255), unique=True, nullable=True, index=True)

    # Basic Information Fields
    company_name = Column(String(255), nullable=False)
    logo_url = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    description = Column(String(2000), nullable=True)
    founded_date = Column(Date, nullable=True)
    annual_revenue = Column(String(100), nullable=True)

    # Contact Details Fields
    location = Column(String(255), nullable=True)
    full_address = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone_code = Column(String(20), nullable=True)
    phone_no = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    twitter_url = Column(String(255), nullable=True)
    instagram_url = Column(String(255), nullable=True)

    # Classification Fields
    account_type = Column(String(100), nullable=False)
    client_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=True)
    segment = Column(String(100), nullable=True)
    territory = Column(String(100), nullable=True)
    source = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)

    # Relationships Fields
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner_name = Column(String(100), default="Admin")
    is_subsidiary = Column(Boolean, default=False)
    parent_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)

    # Keep until confirmed
    is_child_account = Column(Boolean, default=False)
    created_by = Column(String, nullable=True)

    # System Fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Metrics & Activity Tracking
    last_activity_date = Column(DateTime, nullable=True)
    total_revenue = Column(String(255), nullable=True)

    # Relationships
    parent_account = relationship("Account", remote_side=[id], backref="child_accounts")
    contacts = relationship("Lead", secondary="lead_accounts", back_populates="accounts", lazy="select")
    interactions = relationship("Interaction", back_populates="account", lazy="select")
    affiliate_installs = relationship("AffiliateInstall", back_populates="client_account")