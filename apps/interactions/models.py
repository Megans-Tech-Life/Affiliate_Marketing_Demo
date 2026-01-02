from datetime import datetime, timezone
from enum import Enum 
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

# Different types of interactions
class InteractionType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MESSAGE = "MESSAGE"
    MEETING = "MEETING"
    FOLLOW_UP = "FOLLOW_UP"
    DEMO = "DEMO"
    NOTE = "NOTE"
    OTHER = "OTHER"
    
class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    type = Column(SAEnum(
        InteractionType,
        name="interactiontype",
        native_enum=True,
        validate_strings=True,
        values_callable=lambda enum: [e.value for e in enum]),nullable=False)    
    subject = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    outcome = Column(String(255), nullable=True)
    next_steps = Column(Text, nullable=True)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    occurred_at = Column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc),
)
    created_at = Column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc),
)
    updated_at = Column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
)
    
    # Relationships
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)

    account = relationship("Account", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
    lead = relationship("Lead", back_populates="interactions")
    person = relationship("PersonOfContact", back_populates="interactions")
    followups = relationship("FollowUp", back_populates="interaction")

    is_deleted = Column(Boolean, default=False, nullable=False)

