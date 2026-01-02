from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from core.dependencies import get_db
from apps.auth.security import get_current_user
from .models import Account
from .schemas import AccountNameResponse, AccountResponse, AccountCreate, AccountUpdate
from . import services

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# Create a new account
@router.post("/", response_model=AccountResponse)
def create_account(account_data: AccountCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_account = services.create_account(db, account_data, current_user)
    return new_account

# Get all accounts for logged in user
@router.get("/", response_model=List[AccountResponse])
def get_accounts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return services.get_accounts(db, current_user)

# Get all accounts for parent-child accounts
@router.get("/all-accounts", response_model=List[AccountNameResponse])
def get_all_accounts_for_parent_selection(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)):
    return services.get_all_account_names(db)

# Get all deleted accounts 
@router.get("/trash", response_model=List[AccountResponse])
def get_deleted_accounts(db: Session = Depends(get_db)):
    return services.get_deleted_accounts(db)

# Get a single account by ID
@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: UUID, db: Session = Depends(get_db)):
    account = services.get_account(db, account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account

# Update an existing account 
@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: UUID, account_update: AccountUpdate, db: Session = Depends(get_db)):
    updated = services.update_account(db, account_id, account_update)

    if not updated:
        raise HTTPException(status_code=404, detail="Account not found")

    return updated

# Get contacts for an account
@router.get("/contacts/{account_id}")
def get_account_contacts(account_id: UUID, db: Session = Depends(get_db)):
    contacts = services.get_account_contacts(db, account_id)

    if contacts is None:
        raise HTTPException(status_code=404, detail="Account not found")

    contacts_list = [
        {
            "id": c.id,
            "title": c.title,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone_code": c.phone_code,
            "phone_no": c.phone_no,
            "created_at": c.created_at,
        }
        for c in contacts
    ]

    return {
        "account_id": str(account_id),
        "total_contacts": len(contacts_list),
        "contacts": contacts_list,
    }

# Soft delete
@router.delete("/{account_id}", response_model=dict)
def delete_account(account_id: UUID, db: Session = Depends(get_db)):
    deleted = services.soft_delete_account(db, account_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")

    return {"message": f"Account {account_id} moved to trash successfully"}

# Restore account from trash
@router.put("/restore/{account_id}", response_model=AccountResponse)
def restore_account(account_id: UUID, db: Session = Depends(get_db)):
    restored = services.restore_account(db, account_id)

    if not restored:
        raise HTTPException(status_code=404, detail="Account not found or not deleted")

    return restored