import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, String, DateTime, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from apps.transactions.models import CommissionRecord

person_leads = Table(
    "person_leads",
    Base.metadata,
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id")),
    Column("lead_id", UUID(as_uuid=True), ForeignKey("leads.id"))
)

class PersonOfContact(Base):
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Kept for matching logic with leads
    role = Column(String(100), nullable=True)
    personality_type = Column(String(50), nullable=True)

    is_deleted = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship(
        "User", 
        back_populates="person", 
        lazy="joined"
    )

    leads = relationship(
        "Lead",
        secondary="person_leads",
        back_populates="persons"
    )

    products = relationship(
        "Product",
        secondary="product_persons",
        back_populates="persons"
    )

    opportunities = relationship(
        "Opportunity",
        secondary="opportunity_persons",
        back_populates="persons"
    )

    interactions = relationship(
        "Interaction",
        back_populates="person"
    )

    commissions = relationship(
        "CommissionRecord",
        back_populates="salesperson"
    )

    followups = relationship(
        "FollowUp", 
        back_populates="person"
    )
    
    performance_records = relationship(
        "PerformanceRecord",
        back_populates="person"
    )

    wallet = relationship(
        "Wallet", 
        back_populates="person", 
        uselist=False
    )
    
    withdrawal_requests = relationship(
        "WithdrawalRequest", 
        back_populates="requested_by"
    )