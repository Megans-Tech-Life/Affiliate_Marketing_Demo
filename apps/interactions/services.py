from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging
from . import models, schemas
from .models import Interaction
from apps.leads.models import Lead
from uuid import UUID
from enum import Enum

logger = logging.getLogger(__name__)

def create_interaction(
    db: Session,
    interaction: schemas.InteractionCreate,
    created_by: UUID
):
    data = interaction.model_dump(exclude_unset=True)
    if isinstance(data.get("type"), Enum):
        data["type"] = data["type"].value

    data["occurred_at"] = data.get("occurred_at", datetime.now(timezone.utc))

    new_interaction = models.Interaction(
        **data,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(new_interaction)
    # Update last_contact_at on Lead
    if new_interaction.lead_id:
        lead = (
            db.query(Lead)
            .filter(Lead.id == new_interaction.lead_id)
            .first()
        )
        if lead:
            lead.last_contact_at = datetime.now(timezone.utc)
            if lead.status == "New":
               lead.status = "Contacted"
    db.commit()
    db.refresh(new_interaction)
    return new_interaction

def get_all_interactions(db: Session, skip: int = 0, limit: int =100, include_deleted: bool = False):
    query = db.query(models.Interaction)
    if not include_deleted:
        query = query.filter(models.Interaction.is_deleted.is_(False))
    return query.offset(skip).limit(limit).all()

def get_interaction_by_id(db: Session, interaction_id: int):
    return db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()

def update_interaction(
    db: Session,
    interaction_id: int,
    interaction_data: schemas.InteractionUpdate
):
    interaction = (
        db.query(models.Interaction)
        .filter(models.Interaction.id == interaction_id)
        .first()
    )
    if not interaction:
        return None

    update_data = interaction_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if hasattr(interaction, key):
            setattr(interaction, key, value)

    interaction.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(interaction)
    return interaction


def soft_delete_interaction(db: Session, interaction_id: int):
    interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if not interaction:
        return None
    
    interaction.is_deleted = True
    interaction.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(interaction)
    return interaction

def restore_interaction(db: Session, interaction_id: int):
    interaction = (db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first())
    if not interaction:
        return None # Not found
    
    if not interaction.is_deleted:
        return interaction  # Already active

    interaction.is_deleted = False
    interaction.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(interaction)
    return interaction

def get_deleted_interactions(db: Session, skip: int = 0, limit: int = 100):
    return (db.query(models.Interaction)
            .filter(models.Interaction.is_deleted.is_(True))
            .offset(skip)
            .limit(limit)
            .all())