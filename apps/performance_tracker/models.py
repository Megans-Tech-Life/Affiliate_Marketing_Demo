from sqlalchemy import Column, Float, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from core.database import Base

class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))
    total_leads = Column(Integer, default=0)
    total_opportunities = Column(Integer, default=0)
    closed_deals = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    total_commission = Column(Float, default=0.0)
    recorded_at = Column(DateTime, default=datetime.now(timezone.utc))

    person = relationship("PersonOfContact", back_populates="performance_records")
