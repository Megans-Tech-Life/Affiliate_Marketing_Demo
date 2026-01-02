from sqlalchemy.orm import Session
from fastapi import logger
from . import models, schemas
from apps.leads.models import Lead
from apps.leads.services import convert_lead_to_contact
from apps.contacts.models import PersonOfContact
from apps.products.models import Product

def create_opportunity(db: Session, opportunity: schemas.OpportunityCreate):
    db_opportunity = models.Opportunity(
        name=opportunity.name,
        description=opportunity.description,
        stage=opportunity.stage,
        status=opportunity.status,
        price_value=opportunity.price_value
    )
    # Attach leads + convert to contact
    if opportunity.leads_ids:
        leads = db.query(Lead).filter(Lead.id.in_(opportunity.leads_ids)).all()
        db_opportunity.leads = leads
        for lead in leads:
            if not lead.is_contact:
               convert_lead_to_contact(db, lead.id)
    # Attach persons of contact
    if opportunity.poc_ids:
        db_opportunity.persons = db.query(PersonOfContact).filter(
            PersonOfContact.id.in_(opportunity.poc_ids)).all()
    # Attach products
    if opportunity.products_ids:
        db_opportunity.products = db.query(Product).filter(
            Product.id.in_(opportunity.products_ids)).all()

    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

# Retrieve all opportunities
def get_opportunities(db: Session):
    return db.query(models.Opportunity).filter(models.Opportunity.is_deleted == False).all()

# Retrieve a single opportunity by ID
def get_opportunity(db: Session, opportunity_id: str):
    return db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()

# Update an existing opportunity
def update_opportunity(db: Session, opportunity_id: str, opportunity_data: schemas.OpportunityUpdate):
    db_opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not db_opportunity:
        return None
    
    data = opportunity_data.model_dump(exclude_unset=True)
    unsupported_fields = []
    
    # Update main fields with defensive pattern
    for key, value in data.items():
        if key not in ["leads_ids", "poc_ids", "products_ids"]:
            if hasattr(db_opportunity, key):
                setattr(db_opportunity, key, value)
            else:
                unsupported_fields.append(key)
    
    if unsupported_fields:
        logger.warning(
            f"Unsupported fields received in opportunity update: {unsupported_fields}"
        )
    
    # Update leads + convert new leads to contacts
    if "leads_ids" in data:
        new_leads = db.query(Lead).filter(Lead.id.in_(data["leads_ids"])).all()
        db_opportunity.leads = new_leads
        
        for lead in new_leads:
            if not lead.is_contact:
               convert_lead_to_contact(db, lead.id)
    # Update persons of contact
    if "poc_ids" in data:
        db_opportunity.persons = db.query(PersonOfContact).filter(
            PersonOfContact.id.in_(data["poc_ids"])).all()    
    # Update products
    if "products_ids" in data:
        db_opportunity.products = db.query(Product).filter(
            Product.id.in_(data["products_ids"])).all()
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

# Soft Delete an opportunity
def soft_delete_opportunity(db: Session, opportunity_id: str):
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if opportunity:
        opportunity.is_deleted = True
        db.commit()
        db.refresh(opportunity)
    return opportunity

# Get Deleted Opportunities from Trash
def get_deleted_opportunities(db: Session):
    return db.query(models.Opportunity).filter(models.Opportunity.is_deleted == True).all()

# Restore a soft-deleted opportunity
def restore_opportunity(db: Session, opportunity_id: str):
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if opportunity:
        opportunity.is_deleted = False
        db.commit()
        db.refresh(opportunity)
    return opportunity