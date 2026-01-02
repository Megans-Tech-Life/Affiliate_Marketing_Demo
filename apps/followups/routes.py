from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from apps.followups import models, schemas, services
from apps.auth.models import User
from core.database import get_db
from apps.auth.security import get_current_user 

router = APIRouter(
    prefix="/followups",
    tags=["Follow-Ups"],
)

# Create Follow-Up
@router.post("/", response_model=schemas.FollowUpResponse)
def create_followup(
    data: schemas.FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.create_followup(db, data, current_user)


# Get All Active Follow-Ups
@router.get("/", response_model=List[schemas.FollowUpResponse])
def get_all_followups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.get_all_followups(db, current_user)

# Get All Deleted Follow-Ups from Trash
@router.get("/trash", response_model=List[schemas.FollowUpResponse])
def get_deleted_followups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.get_deleted_followups(db, current_user)


# Get Past Due Follow-Ups
@router.get("/reminders/past-due", response_model=List[schemas.FollowUpResponse])
def get_past_due_followups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.get_past_due_followups(db, current_user)


# Get Upcoming Follow-Ups
@router.get("/reminders/upcoming", response_model=List[schemas.FollowUpResponse])
def get_upcoming_followups(
    hours: int = 48,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.get_upcoming_followups(db, current_user, hours)

# Get Follow-Ups with No Recent Interactions
@router.get("/reminders/no-interaction", response_model=List[schemas.FollowUpResponse])
def get_no_interaction_followups(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.get_no_interaction_followups(db, current_user, days)

# Get Follow-Up by ID
@router.get("/{followup_id}", response_model=schemas.FollowUpResponse)
def get_followup_by_id(
    followup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.get_followup_by_id(db, followup_id, current_user)

# Update Follow-Up
@router.put("/{followup_id}", response_model=schemas.FollowUpResponse)
def update_followup(
    followup_id: str,
    data: schemas.FollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.update_followup(db, followup_id, data, current_user)


# Soft Delete Follow-Up
@router.delete("/{followup_id}", response_model=schemas.FollowUpResponse)
def soft_delete_followup(
    followup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.soft_delete_followup(db, followup_id, current_user)


# Restore Soft-Deleted Follow-Up
@router.put("/restore/{followup_id}", response_model=schemas.FollowUpResponse)
def restore_followup(
    followup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.restore_followup(db, followup_id, current_user)

