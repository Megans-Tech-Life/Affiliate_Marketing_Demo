from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from apps.leads.models import Lead
from apps.products.models import Product
from apps.auth.models import User
from apps.opportunities.models import Opportunity
from .models import PersonOfContact
import logging

logger = logging.getLogger(__name__)

# Create a new Person of Contact
def create_poc(db: Session, poc_data: schemas.POCCreate, current_user: User):
    db_poc = models.PersonOfContact(
        role=poc_data.role,
        personality_type=poc_data.personality_type,
        is_deleted=poc_data.is_deleted or False,
        user_id=current_user.id,
    )

    # Attach relationships if provided
    if poc_data.leads_ids:
        db_poc.leads = db.query(Lead).filter(Lead.id.in_(poc_data.leads_ids)).all()

    if poc_data.products_ids:
        db_poc.products = db.query(Product).filter(Product.id.in_(poc_data.products_ids)).all()

    if poc_data.opportunities_ids:
        db_poc.opportunities = db.query(Opportunity).filter(Opportunity.id.in_(poc_data.opportunities_ids)).all()

    # Save to DB
    db.add(db_poc)
    db.commit()
    db.refresh(db_poc)
    return db_poc


# Get all Persons of Contact (non-deleted)
def get_all_pocs(db: Session, include_deleted: bool = False):
    query = db.query(models.PersonOfContact)
    if not include_deleted:
        query = query.filter(models.PersonOfContact.is_deleted == False)
    return query.all()


# Get a single Person by ID
def get_poc_by_id(db: Session, poc_id: str):
    poc = db.query(models.PersonOfContact).filter(models.PersonOfContact.id == poc_id).first()
    if not poc:
        raise HTTPException(status_code=404, detail="Contact not found")
    return poc


# Update an existing Person
def update_poc(db: Session, poc_id: str, poc_data: schemas.POCUpdate):
    db_poc = db.query(models.PersonOfContact).filter(models.PersonOfContact.id == poc_id).first()
    if not db_poc:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = poc_data.model_dump(exclude_unset=True)
    unsupported_fields = []

    for key, value in update_data.items():
        if key in ["lead_ids", "product_ids", "opportunity_ids"]:
            # Handle relationship updates separately
            if key == "lead_ids":
                db_poc.leads = db.query(Lead).filter(Lead.id.in_(value)).all() if value else []
            elif key == "product_ids":
                db_poc.products = db.query(Product).filter(Product.id.in_(value)).all() if value else []
            elif key == "opportunity_ids":
                db_poc.opportunities = db.query(Opportunity).filter(Opportunity.id.in_(value)).all() if value else []
        else:
            if hasattr(db_poc, key):
                setattr(db_poc, key, value)
            else:
                unsupported_fields.append(key)
    
    if unsupported_fields:
        logger.warning(
            f"Unsupported fields received in contact update: {unsupported_fields}"
        )

    db.commit()
    db.refresh(db_poc)
    return db_poc


# Soft delete
def soft_delete_poc(db: Session, poc_id: str):
    db_poc = db.query(models.PersonOfContact).filter(models.PersonOfContact.id == poc_id).first()
    if not db_poc:
        raise HTTPException(status_code=404, detail="Contact not found")

    db_poc.is_deleted = True
    db.commit()
    return {"message": "Contact moved to trash successfully"}


# Restore from soft delete
def restore_poc(db: Session, poc_id: str):
    db_poc = db.query(models.PersonOfContact).filter(models.PersonOfContact.id == poc_id).first()
    if not db_poc:
        raise HTTPException(status_code=404, detail="Contact not found")

    db_poc.is_deleted = False
    db.commit() 
    db.refresh(db_poc)
    return db_poc

# Get all soft-deleted Persons of Contact
def get_deleted_pocs(db: Session):
    return db.query(PersonOfContact).filter(PersonOfContact.is_deleted == True).all()