from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from . import schemas, services

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

# Create a new Opportunity
@router.post("/", response_model=schemas.OpportunityResponse)
def create_opportunity(opportunity: schemas.OpportunityCreate, db: Session = Depends(get_db)):
    return services.create_opportunity(db, opportunity)

# Get all Opportunities
@router.get("/", response_model=list[schemas.OpportunityResponse])
def get_opportunities(db: Session = Depends(get_db)):
    return services.get_opportunities(db)

# Get deleted Opportunities
@router.get("/trash", response_model=list[schemas.OpportunityResponse])
def get_deleted_opportunities(db: Session = Depends(get_db)):
    return services.get_deleted_opportunities(db)

# Get, Update, Delete an Opportunity by ID
@router.get("/{opportunity_id}", response_model=schemas.OpportunityResponse)
def get_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    db_opportunity = services.get_opportunity(db, opportunity_id)
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return db_opportunity

@router.put("/{opportunity_id}", response_model=schemas.OpportunityResponse)
def update_opportunity(opportunity_id: str, opportunity_update: schemas.OpportunityUpdate, db: Session = Depends(get_db)):
    updated_opportunity = services.update_opportunity(db, opportunity_id, opportunity_update)
    if not updated_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return updated_opportunity

@router.delete("/{opportunity_id}")
def delete_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    db_opportunity = services.soft_delete_opportunity(db, opportunity_id)
    if not db_opportunity: 
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return {"message": "Opportunity moved to trash successfully"}

# Restore an Opportunity from trash
@router.put("/restore/{opportunity_id}", response_model=schemas.OpportunityResponse)
def restore_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    restored_opportunity = services.restore_opportunity(db, opportunity_id)
    if not restored_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return restored_opportunity
