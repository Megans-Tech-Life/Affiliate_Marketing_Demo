from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from . import services, schemas, models
from apps.auth.security import get_current_user

router = APIRouter(prefix="/interactions", tags=["interactions"])

# Create Interaction
@router.post("/", response_model=schemas.InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_interaction(
    interaction: schemas.InteractionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    created_by = current_user.id  # Get user UUID from JWT

    new_interaction = services.create_interaction(
        db=db,
        interaction=interaction,
        created_by=created_by
    )

    return new_interaction


# Get All Interactions (not deleted)
@router.get("/", response_model=List[schemas.InteractionResponse])
def get_all_interactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    interactions = services.get_all_interactions(db)
    return interactions

# Get Deleted Interaction from Trash
@router.get("/trash", response_model=List[schemas.InteractionResponse])
def get_deleted_interactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    deleted = services.get_deleted_interactions(db)
    return deleted

# Get Interaction by ID
@router.get("/{interaction_id}", response_model=schemas.InteractionResponse)
def get_interaction_by_id(
    interaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    interaction = services.get_interaction_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


# Update Interaction
@router.put("/{interaction_id}", response_model=schemas.InteractionResponse)
def update_interaction(
    interaction_id: UUID,
    interaction_update: schemas.InteractionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    updated_interaction = services.update_interaction(db, interaction_id, interaction_update)
    if not updated_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return updated_interaction


# Soft Delete Interaction
@router.delete("/{interaction_id}")
def soft_delete_interaction(
    interaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    deleted = services.soft_delete_interaction(db, interaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interaction not found or already deleted")
    return {"message": f"Interaction {interaction_id} moved to trash."}


# Restore Interaction
@router.put("/restore/{interaction_id}")
def restore_interaction(
    interaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    restored = services.restore_interaction(db, interaction_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Interaction not found or not deleted")
    return {"message": f"Interaction {interaction_id} restored successfully."}
