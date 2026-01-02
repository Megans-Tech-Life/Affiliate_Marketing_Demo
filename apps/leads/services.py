import datetime
from sqlalchemy import and_, exists, or_
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from fastapi import HTTPException, logger
from apps.accounts.models import Account
from apps.contacts.models import PersonOfContact, person_leads
from .models import Lead, LeadProduct
from .models import lead_accounts, LeadDetails
from .schemas import LeadCreate, LeadUpdate
import logging
from apps.leads.scoring import resolve_lead_score

logger = logging.getLogger(__name__)

# Create leads
def create_lead_service(db: Session, lead_data: LeadCreate):
    data = lead_data.model_dump()

    stage = data.get("lead_stage")
    substage = data.get("lead_substage")
    data["score"] = resolve_lead_score(stage, substage)

    details_data = data.pop("details", None)
    products = data.pop("products", None)
    account_ids = data.pop("account_ids", None)

    if 'company' in data:
        data['company_name'] = data.pop('company')

    try:
        lead = Lead(**data)
        db.add(lead)
        db.flush()
        # Create LeadDetails
        if details_data:
            lead_details = LeadDetails(lead_id=lead.id, **details_data)
            db.add(lead_details)

        # Associate Accounts
        if account_ids:
            accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()
            lead.accounts = accounts

        # Associate Products
        if products:
            lead_products = [
                LeadProduct(lead_id=lead.id, product=product)
                for product in products
            ]
            db.add_all(lead_products)

        db.commit()
        lead = (
            db.query(Lead)
            .options(joinedload(Lead.accounts))
            .filter(Lead.id == lead.id)
            .first()
        )
        lead.account_ids = [a.id for a in lead.accounts]
        return lead
    except Exception:
        db.rollback()
        raise

# Retrieve leads
def get_lead_service(db: Session, lead_id: str):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

# Check if Lead exists based on email and phone number
def validate_lead_existence(
    db: Session, 
    poc_id: str = None,
    account_email: str = None, 
    account_phone_no: str = None, 
    account_phone_code: str = None
):
    existing_poc = None
    if poc_id:
        existing_poc = db.query(PersonOfContact).filter(
            PersonOfContact.id == poc_id
        ).first()

    existing_account = db.query(Account).filter(
        or_(
            Account.email == account_email,
            and_(
                Account.phone_no == account_phone_no,
                Account.phone_code == account_phone_code
            )
        )
    ).first()

    # If both exist, check if any Lead connects to BOTH
    if existing_poc and existing_account:
        duplicate_lead = (
            db.query(Lead)
            .filter(
                exists().where(
                    and_(
                        lead_accounts.c.lead_id == Lead.id,
                        lead_accounts.c.account_id == existing_account.id
                    )
                ),
                exists().where(
                    and_(
                        person_leads.c.lead_id == Lead.id,
                        person_leads.c.person_id == existing_poc.id
                    )
                ),
            )
            .first()
        )
        if duplicate_lead:
            raise HTTPException(
                status_code=400, 
                detail="Lead with the given contact details already exists."
            )
    return {"message": "No duplicate lead found."}

# Convert lead to contact
def convert_lead_to_contact(db: Session, lead_id: UUID):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = "Converted"
    lead.is_contact = True
    db.commit()
    db.refresh(lead)
    return lead

def update_lead_service(db: Session, lead_id: str, lead_data: LeadUpdate):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    data = lead_data.model_dump(exclude_unset=True)
    
    details_data = data.pop("details", None)
    products = data.pop("products", None)

    if "company" in data:
        data["company_name"] = data.pop("company")

    # Track scoring-related changes
    stage_changed = False
    new_stage = lead.lead_stage
    new_substage = lead.lead_substage

    if "lead_stage" in data:
        new_stage = data["lead_stage"]
        stage_changed = True

    if "lead_substage" in data:
        new_substage = data["lead_substage"]
        stage_changed = True

    try:
        # Update main Lead fields
        for key, value in data.items():
            if hasattr(lead, key):
                setattr(lead, key, value)

        # Contact info validation
        final_email = data["email"] if "email" in data else lead.email
        final_phone_no = data["phone_no"] if "phone_no" in data else lead.phone_no
        final_phone_code = data["phone_code"] if "phone_code" in data else lead.phone_code
        has_email = bool(final_email)
        has_phone = bool(final_phone_code and final_phone_no)
        if not (has_email or has_phone):
            raise HTTPException(status_code=400, detail="Either email or complete phone number must be provided.")

        # Recalculate score only if stage/substage changed
        if stage_changed:
            lead.score = resolve_lead_score(new_stage, new_substage)

        # Update LeadDetails if provided
        if details_data:
            if lead.details:
                for key, value in details_data.items():
                    if hasattr(lead.details, key):
                        setattr(lead.details, key, value)
            else:
                db.add(LeadDetails(lead_id=lead.id, **details_data))
                

        # Update products
        if products is not None:
            db.query(LeadProduct).filter(LeadProduct.lead_id == lead.id).delete()
            db.add_all([LeadProduct(lead_id=lead.id, product=product) for product in products])
             
        db.commit()
        db.refresh(lead)
        return lead

    except Exception:
        db.rollback()
        raise

def soft_delete_lead_service(db: Session, lead_id: str):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        lead.is_deleted = True
        db.commit()
        db.refresh(lead)
    return lead

def restore_lead_service(db: Session, lead_id: str):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead and lead.is_deleted:
        lead.is_deleted = False
        db.commit()
        db.refresh(lead)
        return lead
    return None

