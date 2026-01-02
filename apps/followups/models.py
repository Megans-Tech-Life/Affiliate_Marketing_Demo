from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    Table,
)
from sqlalchemy.orm import relationship
from core.database import Base


followup_assignees = Table(
    "followup_assignees",
    Base.metadata,
    Column(
        "followup_id",
        UUID(as_uuid=True),
        ForeignKey("followups.id"),
        primary_key=True,
    ),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    ),
)

class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    due_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    type = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)

    # Relationships
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=True)
    poc_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.id"), nullable=False)

    # Many-to-many: assigned users
    assigned_users = relationship(
        "User",
        secondary="followup_assignees",
        back_populates="followups"
    )

    lead = relationship("Lead", back_populates="followups")
    opportunity = relationship("Opportunity", back_populates="followups")
    person = relationship("PersonOfContact", back_populates="followups")
    interaction = relationship("Interaction", back_populates="followups")

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Computed properties past due and upcoming
    @property
    def is_past_due(self) -> bool:
        if self.is_deleted or self.status == "completed" or not self.due_date:
            return False
        due_date = (
            self.due_date.replace(tzinfo=timezone.utc)
            if self.due_date.tzinfo is None
            else self.due_date
        )
        return due_date < datetime.now(timezone.utc)
    
    
    def is_upcoming(self, hours: int = 48) -> bool:

        if self.is_deleted or self.status == "completed" or not self.due_date:
            return False

        now = datetime.now(timezone.utc)
        due_date = (
            self.due_date.replace(tzinfo=timezone.utc)
            if self.due_date.tzinfo is None
            else self.due_date
        )
        return now <= due_date <= now + timedelta(hours=hours)
