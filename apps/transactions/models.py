from sqlalchemy import Column, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from core.database import Base
import enum

class CommissionStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    canceled = "canceled"

class CommissionRecord(Base):
    __tablename__ = "commission_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    salesperson_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=True)
    amount = Column(Float, nullable=False)
    percentage = Column(Float, nullable=True)
    status = Column(Enum(CommissionStatus), default=CommissionStatus.pending)
    payment_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    salesperson = relationship("PersonOfContact", back_populates="commissions", lazy="joined")
    opportunity = relationship("Opportunity", back_populates="commissions", lazy="joined")