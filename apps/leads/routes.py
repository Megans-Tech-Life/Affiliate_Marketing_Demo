from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from apps.auth.security import get_current_user
from core.database import get_db
from .models import Lead
from .schemas import LeadResponse, LeadCreate, LeadUpdate, LeadValidationRequest, LeadConvertResponse
from .services import (
    convert_lead_to_contact, 
    validate_lead_existence,
    create_lead_service,
    update_lead_service,
    soft_delete_lead_service,
    restore_lead_service
)
from apps.accounts.models import Account
from apps.auth.models import User
from apps.leads import schemas

router = APIRouter(prefix="/leads", tags=["Leads"])

# Create Lead
@router.post("/", response_model=LeadResponse)
def create_lead(lead: LeadCreate, 
                db: Session = Depends(get_db), 
                current_user: dict = Depends(get_current_user)):
    new_lead = create_lead_service(db, lead)
    return new_lead

# Validate Lead
@router.post("/validate", response_model=dict)
def validate_lead(
    request: schemas.LeadValidationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = validate_lead_existence(
        db=db,
        poc_id=request.poc_id,
        account_email=request.account_email,
        account_phone_no=request.account_phone_no,
        account_phone_code=request.account_phone_code
    )
    return result

# Get Leads
@router.get("/", response_model=List[LeadResponse])
def get_leads(db: Session = Depends(get_db), 
              current_user: dict = Depends(get_current_user)):
    return db.query(Lead).filter(Lead.is_deleted.is_(False)).all()

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: UUID, db: Session = Depends(get_db), 
             current_user: dict = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

# Update Lead
@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: UUID, lead_update: LeadUpdate, db: Session = Depends(get_db), 
                current_user: dict = Depends(get_current_user)):
    updated_lead = update_lead_service(db, lead_id, lead_update)
    if not updated_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated_lead

# NOTE: Contacts here are Lead entities linked to an Account
# Lead to contact conversion happens explicitly in opportunity or convert endpoint
# Get, Add, Remove Contacts(Leads) for an Account
@router.get("/contacts/account/{account_id}", response_model=List[LeadResponse])
def get_account_contacts(account_id: UUID, db: Session = Depends(get_db), 
                         current_user: dict = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.contacts

@router.post("/contacts/account/{account_id}/lead/{lead_id}", response_model=dict)
def add_contact_to_account(account_id: UUID, lead_id: UUID, db: Session = Depends(get_db),
                           current_user: dict = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead not in account.contacts:
        account.contacts.append(lead)
        db.commit()
        return {"message": f"Lead {lead_id} linked to account {account_id}"}
    else:
        return {"message": "Lead already linked to this contact"}

@router.delete("/contacts/account/{account_id}/lead/{lead_id}", response_model=dict)
def remove_contact_from_account(account_id: UUID, lead_id: UUID, db: Session = Depends(get_db),
                                current_user: dict = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead in account.contacts:
        account.contacts.remove(lead)
        db.commit()
        return {"message": "Lead unlinked from account"}
    else:
        return {"message": "Lead is not linked to this account"}

# Convert Lead to Contact
@router.post("/{lead_id}/convert", response_model=LeadConvertResponse)
def convert_lead(lead_id: UUID, db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    lead = convert_lead_to_contact(db, lead_id)
    return {
        "message": f"Lead {lead_id} converted to contact successfully",
        "lead": lead
    }

# Transfer Lead Ownership
@router.put("/{lead_id}/transfer/{new_user_id}", response_model=dict)
def transfer_lead_ownership(lead_id: UUID, new_user_id: UUID, db: Session = Depends(get_db),
                            current_user: dict = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    new_owner = db.query(User).filter(User.id == new_user_id).first()
    if not new_owner:
        raise HTTPException(status_code=404, detail="User not found")

    lead.user_id = new_user_id
    db.commit()
    db.refresh(lead)

    return {"message": "Lead ownership transferred"}

# Soft Delete, get from Trash, Restore Lead from Trash
@router.delete("/trash/{lead_id}", response_model=dict)
def soft_delete_lead(lead_id: UUID, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    lead = soft_delete_lead_service(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead moved to trash"}

@router.get("/trash/", response_model=List[LeadResponse])
def get_deleted_leads(db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    return db.query(Lead).filter(Lead.is_deleted.is_(True)).all()

@router.put("/restore/{lead_id}", response_model=dict)
def restore_lead(lead_id: UUID, db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    lead = restore_lead_service(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found or not in trash")
    return {"message": "Lead restored"}
