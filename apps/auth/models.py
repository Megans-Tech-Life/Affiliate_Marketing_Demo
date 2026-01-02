import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone_code = Column(String(20), nullable=True)
    phone_no = Column(String(50), nullable=True)

    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # relationships
    person = relationship("PersonOfContact", back_populates="user", uselist=False)
    followups = relationship(
        "FollowUp",
        secondary="followup_assignees",
        back_populates="assigned_users"
    )
    leads = relationship("Lead", back_populates="user")
    interactions = relationship("Interaction", back_populates="user")
    affiliate_clicks = relationship("AffiliateClick", back_populates="affiliate_user")
    affiliate_installs = relationship("AffiliateInstall", back_populates="affiliate_user")
    affiliate_referrals = relationship("AffiliateReferral", back_populates="affiliate_user")
    affiliate_links = relationship("AffiliateLink", back_populates="affiliate_user")
    
