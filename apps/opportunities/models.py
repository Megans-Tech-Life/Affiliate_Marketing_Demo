import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Date, String, DateTime, Float, Table, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from core.database import Base
from apps.transactions.models import CommissionRecord

# Association tables for Many-to-Many relationships
opportunity_leads = Table(
    "opportunity_leads",
    Base.metadata,
    Column("opportunity_id", UUID(as_uuid=True), ForeignKey("opportunities.id")),
    Column("lead_id", UUID(as_uuid=True), ForeignKey("leads.id"))
)

opportunity_products = Table(
    "opportunity_products",
    Base.metadata,
    Column("opportunity_id", UUID(as_uuid=True), ForeignKey("opportunities.id")),
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"))
)

opportunity_persons = Table(
    "opportunity_persons",
    Base.metadata,
    Column("opportunity_id", UUID(as_uuid=True), ForeignKey("opportunities.id")),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id"))
)


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stage = Column(String(100), nullable=True)
    status = Column(String(50), default="open")
    price_value = Column(JSON, nullable=True)
 
    # Win/loss analysis
    expected_close_date = Column(Date, nullable=True)
    reason_lost = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    is_deleted = Column(Boolean, default=False)

    # Relationships
    leads = relationship("Lead", secondary=opportunity_leads, back_populates="opportunities")
    persons = relationship("PersonOfContact", secondary=opportunity_persons, back_populates="opportunities")
    products = relationship("Product", secondary=opportunity_products, back_populates="opportunities")
    commissions = relationship("CommissionRecord", back_populates="opportunity")
    followups = relationship("FollowUp", back_populates="opportunity")