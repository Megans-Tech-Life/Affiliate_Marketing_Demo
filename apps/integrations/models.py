import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
   
    affiliate_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # e-commerce store domain
    shop_domain = Column(String(255), nullable=False, index=True)
    
    # For debugging / should match with affiliate_user_id
    utm_source = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    affiliate_user = relationship("User", back_populates="affiliate_clicks")

class AffiliateLink(Base):
    __tablename__ = "affiliate_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    affiliate_user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    tracking_url = Column(String(512), nullable=False, unique=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    affiliate_user = relationship("User", back_populates="affiliate_links")
    leads = relationship("Lead", back_populates="affiliate_link", lazy="joined")
    
class AffiliateInstall(Base):
    __tablename__ = "affiliate_installs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    affiliate_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    affiliate_link_id = Column(UUID(as_uuid=False), ForeignKey("affiliate_links.id"), nullable=True, index=True)
    lead_id = Column(UUID(as_uuid=False), ForeignKey("leads.id"), nullable=True, index=True)

    shop_domain = Column(String(255), nullable=True, index=True)
    client_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True, index=True)

    installed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    converted_at = Column(DateTime(timezone=True), nullable=True)

    # Prevent duplicate emails
    admin_notified_at = Column(DateTime(timezone=True), nullable=True)
    affiliate_notified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    affiliate_user = relationship("User", back_populates="affiliate_installs")
    affiliate_link = relationship("AffiliateLink")
    lead = relationship("Lead")
    client_account = relationship("Account", back_populates="affiliate_installs")

class AffiliateReferral(Base):
    __tablename__ = "affiliate_referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    affiliate_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    shop_domain = Column(String(255), nullable=False, index=True)
    
    # Most recent click time attached to this referral
    last_click_id = Column(UUID(as_uuid=True), ForeignKey("affiliate_clicks.id"), nullable=True)
    last_clicked_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(50), default="pending") # pending, installed, converted
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    affiliate_user = relationship("User", back_populates="affiliate_referrals")
    last_click = relationship("AffiliateClick", foreign_keys=[last_click_id])