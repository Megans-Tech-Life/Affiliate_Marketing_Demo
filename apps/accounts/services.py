from click import UUID
from sqlalchemy.orm import Session
from fastapi import logger

from apps.auth.models import User
from .models import Account
from .schemas import AccountCreate, AccountUpdate


# Create a new Account
def create_account(db: Session, account_data: AccountCreate, current_user: User):
    data = account_data.model_dump()
    
    # Set ownership fields
    data["owner_id"] = current_user.id
    data["owner_name"] = getattr(current_user, "name", "User")
    data["created_by"] = current_user.email

    # Parent account safety
    if not data.get("is_subsidiary"):
        data["parent_account_id"] = None

    # Convert empty strings to None
    if data.get("parent_account_id") in ("", "string"):
        data["parent_account_id"] = None

    new_account = Account(**data)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account

# Get all accounts for the logged-in user
def get_accounts(db: Session, current_user):
    return db.query(Account).filter(Account.owner_id == current_user.id, Account.is_deleted == False).all()

# Get all accounts names for parent-child accounts
def get_all_account_names(db: Session):
    accounts = (
        db.query(Account)
        .filter(Account.is_deleted == False)
        .order_by(Account.company_name)
        .all()
    )
    return [{"id": account.id, "company_name": account.company_name} for account in accounts]

# Get a single Account by ID
def get_account(db: Session, account_id):
    return db.query(Account).filter(Account.id == account_id).first()

# Update an existing Account
def update_account(db: Session, account_id, account_data: AccountUpdate):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return None

    update_data = account_data.model_dump(exclude_none=True)
    unsupported_fields = []
    
    # Only update the fields that exist on the model
    for key, value in update_data.items():
        if hasattr(account, key):
            setattr(account, key, value)
        else:
            unsupported_fields.append(key)
    
    if unsupported_fields:
        logger.warning(
            f"Unsupported fields received in account update: {unsupported_fields}"
        )

    db.commit()
    db.refresh(account)
    return account

# Get contacts for an Account
def get_account_contacts(db: Session, account_id: UUID):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return None
    return account.contacts

# Soft Delete
def soft_delete_account(db: Session, account_id):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account:
        account.is_deleted = True
        db.commit()
        db.refresh(account)
    return account

# Get Deleted Accounts from Trash
def get_deleted_accounts(db: Session):
    return db.query(Account).filter(Account.is_deleted == True).all()

# Restore Account from Trash
def restore_account(db: Session, account_id):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account and account.is_deleted:
        account.is_deleted = False
        db.commit()
        db.refresh(account)
        return account
    return None
