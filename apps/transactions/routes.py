from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from core.database import get_db
from . import models, schemas, services
from apps.auth.security import get_current_admin, get_current_user
from apps.auth.models import User

router = APIRouter(prefix="/transactions", tags=["Transaction Tracker"])

# Create a new Transaction Record
@router.post("/", response_model=schemas.CommissionResponse)
def create_commission(commission_data: schemas.CommissionCreate, 
                      db: Session = Depends(get_db), 
                      current_user: User = Security(get_current_user)):
    return services.create_commission(db, commission_data, current_user)

# Get all Transaction Records
@router.get("/", response_model=list[schemas.CommissionResponse])
def get_all_commissions(db: Session = Depends(get_db),
                        current_user: User = Security(get_current_user)):
    return services.get_all_commissions(db, current_user)

# Transaction Overview
@router.get("/overview")
def get_commission_overview(db: Session = Depends(get_db),
                            current_user: User = Security(get_current_admin)):
    summary = services.get_commission_overview(db)
    return summary

# Transaction Summary by Salesperson
@router.get("/salesperson/{salesperson_id}")
def get_commission_summary_by_salesperson(salesperson_id: UUID, db: Session = Depends(get_db),
                                          current_user: User = Security(get_current_admin)):
    summary = services.get_commission_summary_by_salesperson(db, salesperson_id)

    # If the salesperson has no transaction records, return a safe empty response
    if not summary or summary["overall"]["total_commissions"] == 0:
        return {
            "salesperson_id": salesperson_id,
            "overall": {"total_commissions": 0, "total_amount": 0},
            "by_status": []
        }

    return summary

# Get, Update, Delete a Transaction Record by ID
@router.get("/{commission_id}", response_model=schemas.CommissionResponse)
def get_commission(commission_id: UUID, db: Session = Depends(get_db),
                   current_user: User = Security(get_current_user)):
    commission = services.get_commission_by_id(db, commission_id, current_user)
    if not commission:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return commission

@router.put("/{commission_id}", response_model=schemas.CommissionResponse)
def update_commission(commission_id: UUID, update_data: schemas.CommissionUpdate, db: Session = Depends(get_db),
                      current_user: User = Security(get_current_user)):
    commission = services.update_commission(db, commission_id, update_data)
    if not commission:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return commission

@router.delete("/{commission_id}")
def delete_commission(commission_id: UUID, db: Session = Depends(get_db),
                       current_user: User = Security(get_current_user)):
    deleted = services.delete_commission(db, commission_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}
