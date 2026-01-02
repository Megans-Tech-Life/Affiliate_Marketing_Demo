from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import HTTPException, status, logger
from sqlalchemy.orm import Session, joinedload
from apps.followups import models, schemas
from apps.auth.models import User             
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.contacts.models import PersonOfContact
from apps.interactions.models import Interaction

# Ensure related entities exist before creating/updating FollowUp
def _validate_relations(db: Session, data: schemas.FollowUpBase):
  
    poc = db.query(PersonOfContact).filter(PersonOfContact.id == data.poc_id).first()
    if not poc:
        raise HTTPException(status_code=404, detail="Person of contact not found.")

    interaction = db.query(Interaction).filter(Interaction.id == data.interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found.")

    lead = None
    if data.lead_id:
        lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found.")

    opportunity = None
    if data.opportunity_id:
        opportunity = db.query(Opportunity).filter(Opportunity.id == data.opportunity_id).first()
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found.")

    return poc, interaction, lead, opportunity

# Retrieve and validate all assigned users by UUID list
def _get_assigned_users(db: Session, user_ids: List[str]) -> List[User]:
  
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    if len(users) != len(set(user_ids)):
        raise HTTPException(status_code=400, detail="One or more assigned users not found.")
    return users

# Check if current user has permission to modify the follow-up
def _permission_check(followup: models.FollowUp, current_user: User):

    if followup.is_deleted:
        raise HTTPException(status_code=400, detail="This follow-up is deleted.")

    if current_user.id not in [u.id for u in followup.assigned_users]:
        raise HTTPException(status_code=403, detail="You are not authorized to modify this follow-up.")

# Create a new Follow-Up
def create_followup(db: Session, data: schemas.FollowUpCreate, current_user: User,) -> schemas.FollowUpResponse:
    poc, interaction, lead, opportunity = _validate_relations(db, data)
    assigned_users = _get_assigned_users(db, data.assigned_user_ids)
    
    if current_user.id not in [user.id for user in assigned_users]:
        raise HTTPException(status_code=403, detail="You must be assigned to the follow-up to create it.")
    
    followup = models.FollowUp(
        due_date=data.due_date,
        status="pending",
        type=data.type,
        notes=data.notes,
        is_deleted=False,
        poc_id=data.poc_id,
        interaction_id=data.interaction_id,
        lead_id=data.lead_id,
        opportunity_id=data.opportunity_id,
    )

    followup.assigned_users = assigned_users

    db.add(followup)
    db.commit()
    db.refresh(followup)

    due_date = (
        followup.due_date.replace(tzinfo=timezone.utc)
        if followup.due_date and followup.due_date.tzinfo is None
        else followup.due_date
    )
    is_past_due = (
        due_date < datetime.now(timezone.utc)
        if due_date
        else False
    )

    return schemas.FollowUpResponse(
        id=followup.id,
        due_date=followup.due_date,
        status=followup.status,
        type=followup.type,
        notes=followup.notes,
        poc_id=followup.poc_id,
        interaction_id=followup.interaction_id,
        lead_id=followup.lead_id,
        opportunity_id=followup.opportunity_id,
        assigned_user_ids=[user.id for user in followup.assigned_users],
        is_deleted=followup.is_deleted,
        is_past_due=is_past_due,
        created_at=followup.created_at,
        updated_at=followup.updated_at,
    )

def get_all_followups(db: Session, current_user: User) -> List[schemas.FollowUpResponse]:
    followups = (
        db.query(models.FollowUp)
        .options(joinedload(models.FollowUp.assigned_users))
        .filter(models.FollowUp.assigned_users.any(User.id == current_user.id))
        .order_by(models.FollowUp.due_date.asc())
        .all()
    )

    responses = []
    for followup in followups:
        due_date = (
            followup.due_date.replace(tzinfo=timezone.utc)
            if followup.due_date and followup.due_date.tzinfo is None
            else followup.due_date
        )
        is_past_due = (
            due_date < datetime.now(timezone.utc)
            if due_date
            else False
        )

        responses.append(
            schemas.FollowUpResponse(
                id=followup.id,
                due_date=followup.due_date,
                status=followup.status,
                type=followup.type,
                notes=followup.notes,
                poc_id=followup.poc_id,
                interaction_id=followup.interaction_id,
                lead_id=followup.lead_id,
                opportunity_id=followup.opportunity_id,
                assigned_user_ids=[user.id for user in followup.assigned_users],
                is_deleted=followup.is_deleted,
                is_past_due=is_past_due,
                created_at=followup.created_at,
                updated_at=followup.updated_at,
            )
        )

    return responses


def get_followup_by_id(db: Session, followup_id: str, current_user: User) -> schemas.FollowUpResponse:
    followup = (db.query(models.FollowUp).options(joinedload(models.FollowUp.assigned_users))
        .filter(models.FollowUp.id == followup_id).first())

    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found.")
    if current_user.id not in [user.id for user in followup.assigned_users]:
        raise HTTPException(status_code=403, detail="You are not authorized to view this follow-up.")

    due_date = (
        followup.due_date.replace(tzinfo=timezone.utc)
        if followup.due_date and followup.due_date.tzinfo is None
        else followup.due_date
    )
    is_past_due = (
        due_date < datetime.now(timezone.utc)
        if due_date
        else False
    )

    return schemas.FollowUpResponse(
        id=followup.id,
        due_date=followup.due_date,
        status=followup.status,
        type=followup.type,
        notes=followup.notes,
        poc_id=followup.poc_id,
        interaction_id=followup.interaction_id,
        lead_id=followup.lead_id,
        opportunity_id=followup.opportunity_id,
        assigned_user_ids=[user.id for user in followup.assigned_users],
        is_deleted=followup.is_deleted,
        is_past_due=is_past_due,
        created_at=followup.created_at,
        updated_at=followup.updated_at,
        completed_at=followup.completed_at,
    )

def update_followup(db: Session, followup_id: str, data: schemas.FollowUpUpdate, current_user: User) -> schemas.FollowUpResponse:
    followup = db.query(models.FollowUp).options(joinedload(models.FollowUp.assigned_users)) \
        .filter(models.FollowUp.id == followup_id).first()

    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found.")
    _permission_check(followup, current_user)

    update_data = data.dict(exclude_unset=True)
    unsupported_fields = []
    
    for field, value in update_data.items():
        if field == "assigned_user_ids":
            # many-to-many relationship update
            new_assignees = _get_assigned_users(db, value)
            followup.assigned_users = new_assignees
        else:
            if hasattr(followup, field):
                setattr(followup, field, value)
            else:
                unsupported_fields.append(field)
    
    if unsupported_fields:
        logger.warning(
            f"Unsupported fields received in followup update: {unsupported_fields}"
        )

    db.commit()
    db.refresh(followup)

    due_date = (
        followup.due_date.replace(tzinfo=timezone.utc)
        if followup.due_date and followup.due_date.tzinfo is None
        else followup.due_date
    )
    is_past_due = (
        due_date < datetime.now(timezone.utc)
        if due_date
        else False
    )

    return schemas.FollowUpResponse(
        id=followup.id,
        due_date=followup.due_date,
        status=followup.status,
        type=followup.type,
        notes=followup.notes,
        poc_id=followup.poc_id,
        interaction_id=followup.interaction_id,
        lead_id=followup.lead_id,
        opportunity_id=followup.opportunity_id,
        assigned_user_ids=[user.id for user in followup.assigned_users],
        is_deleted=followup.is_deleted,
        is_past_due=is_past_due,
        created_at=followup.created_at,
        updated_at=followup.updated_at,
        completed_at=followup.completed_at,
    )

def soft_delete_followup(db: Session, followup_id: str, current_user: User,) -> schemas.FollowUpResponse:
    followup = db.query(models.FollowUp).options(joinedload(models.FollowUp.assigned_users)) \
        .filter(models.FollowUp.id == followup_id).first()

    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found.")

    _permission_check(followup, current_user)

    if followup.is_deleted:
        raise HTTPException(status_code=400, detail="This follow-up is already deleted.")

    followup.is_deleted = True
    followup.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(followup)

    due_date = (
        followup.due_date.replace(tzinfo=timezone.utc)
        if followup.due_date and followup.due_date.tzinfo is None
        else followup.due_date
    )
    is_past_due = (
        due_date < datetime.now(timezone.utc)
        if due_date
        else False
    )

    return schemas.FollowUpResponse(
        id=followup.id,
        due_date=followup.due_date,
        status=followup.status,
        type=followup.type,
        notes=followup.notes,
        poc_id=followup.poc_id,
        interaction_id=followup.interaction_id,
        lead_id=followup.lead_id,
        opportunity_id=followup.opportunity_id,
        assigned_user_ids=[user.id for user in followup.assigned_users],
        is_deleted=followup.is_deleted,
        is_past_due=is_past_due,
        created_at=followup.created_at,
        updated_at=followup.updated_at,
        completed_at=followup.completed_at,
    )

def restore_followup(db: Session, followup_id: str, current_user: User,) -> schemas.FollowUpResponse:
    followup = db.query(models.FollowUp).options(joinedload(models.FollowUp.assigned_users)) \
        .filter(models.FollowUp.id == followup_id).first()
    
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found.")
    
    if current_user.id not in [user.id for user in followup.assigned_users]:
        raise HTTPException(status_code=403, detail="You are not authorized to restore this follow-up.")

    if not followup.is_deleted:
        raise HTTPException(status_code=400, detail="This follow-up is not deleted.")
    
    followup.is_deleted = False
    followup.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(followup)

    due_date = (
        followup.due_date.replace(tzinfo=timezone.utc)
        if followup.due_date and followup.due_date.tzinfo is None
        else followup.due_date
    )
    is_past_due = (
        due_date < datetime.now(timezone.utc)
        if due_date
        else False
    )

    return schemas.FollowUpResponse(
        id=followup.id,
        due_date=followup.due_date,
        status=followup.status,
        type=followup.type,
        notes=followup.notes,
        poc_id=followup.poc_id,
        interaction_id=followup.interaction_id,
        lead_id=followup.lead_id,
        opportunity_id=followup.opportunity_id,
        assigned_user_ids=[user.id for user in followup.assigned_users],
        is_deleted=followup.is_deleted,
        is_past_due=is_past_due,
        created_at=followup.created_at,
        updated_at=followup.updated_at,
        completed_at=followup.completed_at,
    )

def get_deleted_followups(db: Session, current_user: User) -> List[schemas.FollowUpResponse]:
    followups = (
        db.query(models.FollowUp)
        .options(joinedload(models.FollowUp.assigned_users))
        .filter(
            models.FollowUp.is_deleted == True,
            models.FollowUp.assigned_users.any(User.id == current_user.id),
        )
        .order_by(models.FollowUp.updated_at.desc())
        .all()
    )

    responses = []
    for followup in followups:
        due_date = (
            followup.due_date.replace(tzinfo=timezone.utc)
            if followup.due_date and followup.due_date.tzinfo is None
            else followup.due_date
        )
        is_past_due = (
            due_date < datetime.now(timezone.utc)
            if due_date
            else False
        )

        responses.append(
            schemas.FollowUpResponse(
                id=followup.id,
                due_date=followup.due_date,
                status=followup.status,
                type=followup.type,
                notes=followup.notes,
                poc_id=followup.poc_id,
                interaction_id=followup.interaction_id,
                lead_id=followup.lead_id,
                opportunity_id=followup.opportunity_id,
                assigned_user_ids=[user.id for user in followup.assigned_users],
                is_deleted=followup.is_deleted,
                is_past_due=is_past_due,
                created_at=followup.created_at,
                updated_at=followup.updated_at,
                completed_at=followup.completed_at,
            )
        )

    return responses


def get_past_due_followups(db: Session, current_user: User) -> List[schemas.FollowUpResponse]:
    now = datetime.now(timezone.utc)

    followups = (
        db.query(models.FollowUp)
        .options(joinedload(models.FollowUp.assigned_users))
        .filter(
            models.FollowUp.is_deleted == False,
            models.FollowUp.status != "completed",
            models.FollowUp.due_date < now,
            models.FollowUp.assigned_users.any(User.id == current_user.id),
        )
        .order_by(models.FollowUp.due_date.asc())
        .all()
    )

    responses = []
    for followup in followups:
        due_date = (
            followup.due_date.replace(tzinfo=timezone.utc)
            if followup.due_date and followup.due_date.tzinfo is None
            else followup.due_date
        )
        is_past_due = (
            due_date < datetime.now(timezone.utc)
            if due_date
            else False
        )

        responses.append(
            schemas.FollowUpResponse(
                id=followup.id,
                due_date=followup.due_date,
                status=followup.status,
                type=followup.type,
                notes=followup.notes,
                poc_id=followup.poc_id,
                interaction_id=followup.interaction_id,
                lead_id=followup.lead_id,
                opportunity_id=followup.opportunity_id,
                assigned_user_ids=[user.id for user in followup.assigned_users],
                is_deleted=followup.is_deleted,
                is_past_due=is_past_due,
                created_at=followup.created_at,
                updated_at=followup.updated_at,
                completed_at=followup.completed_at,
            )
        )

    return responses


def get_upcoming_followups(db: Session, current_user: User, hours: int = 48) -> List[schemas.FollowUpResponse]:
    now = datetime.now(timezone.utc)
    upcoming_threshold = now + timedelta(hours=hours)

    followups = (
        db.query(models.FollowUp)
        .options(joinedload(models.FollowUp.assigned_users))
        .filter(
            models.FollowUp.is_deleted == False,
            models.FollowUp.status != "completed",
            models.FollowUp.due_date >= now,
            models.FollowUp.due_date <= upcoming_threshold,
            models.FollowUp.assigned_users.any(User.id == current_user.id),
        )
        .order_by(models.FollowUp.due_date.asc())
        .all()
    )

    responses = []
    for followup in followups:
        due_date = (
            followup.due_date.replace(tzinfo=timezone.utc)
            if followup.due_date and followup.due_date.tzinfo is None
            else followup.due_date
        )
        is_past_due = (
            due_date < datetime.now(timezone.utc)
            if due_date
            else False
        )

        responses.append(
            schemas.FollowUpResponse(
                id=followup.id,
                due_date=followup.due_date,
                status=followup.status,
                type=followup.type,
                notes=followup.notes,
                poc_id=followup.poc_id,
                interaction_id=followup.interaction_id,
                lead_id=followup.lead_id,
                opportunity_id=followup.opportunity_id,
                assigned_user_ids=[user.id for user in followup.assigned_users],
                is_deleted=followup.is_deleted,
                is_past_due=is_past_due,
                created_at=followup.created_at,
                updated_at=followup.updated_at,
                completed_at=followup.completed_at,
            )
        )

    return responses


def get_no_interaction_followups(db: Session, current_user: User, days: int = 7) -> List[schemas.FollowUpResponse]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    followups = (
        db.query(models.FollowUp)
        .join(Interaction)
        .options(joinedload(models.FollowUp.assigned_users))
        .filter(
            models.FollowUp.is_deleted == False,
            models.FollowUp.status != "completed",
            models.FollowUp.updated_at < cutoff,
            models.FollowUp.assigned_users.any(User.id == current_user.id),
        )
        .order_by(Interaction.updated_at.asc())
        .all()
    )

    responses = []
    for followup in followups:
        due_date = (
            followup.due_date.replace(tzinfo=timezone.utc)
            if followup.due_date and followup.due_date.tzinfo is None
            else followup.due_date
        )
        is_past_due = (
            due_date < datetime.now(timezone.utc)
            if due_date
            else False
        )

        responses.append(
            schemas.FollowUpResponse(
                id=followup.id,
                due_date=followup.due_date,
                status=followup.status,
                type=followup.type,
                notes=followup.notes,
                poc_id=followup.poc_id,
                interaction_id=followup.interaction_id,
                lead_id=followup.lead_id,
                opportunity_id=followup.opportunity_id,
                assigned_user_ids=[user.id for user in followup.assigned_users],
                is_deleted=followup.is_deleted,
                is_past_due=is_past_due,
                created_at=followup.created_at,
                updated_at=followup.updated_at,
                completed_at=followup.completed_at,
            )
        )

    return responses
