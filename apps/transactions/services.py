from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import logger
from . import models, schemas


def create_commission(db: Session, commission_data: schemas.CommissionCreate):
    new_commission = models.CommissionRecord(**commission_data.dict())
    db.add(new_commission)
    db.commit()
    db.refresh(new_commission)
    return new_commission


def get_all_commissions(db: Session):
    return db.query(models.CommissionRecord).all()


def get_commission_by_id(db: Session, commission_id):
    return db.query(models.CommissionRecord).filter(models.CommissionRecord.id == commission_id).first()


def update_commission(db: Session, commission_id, update_data: schemas.CommissionUpdate):
    commission = get_commission_by_id(db, commission_id)
    if not commission:
        return None
    
    data = update_data.dict(exclude_unset=True)
    unsupported_fields = []
    
    for key, value in data.items():
        if hasattr(commission, key):
            setattr(commission, key, value)
        else:
            unsupported_fields.append(key)
    
    if unsupported_fields:
        logger.warning(
            f"Unsupported fields received in commission update: {unsupported_fields}"
        )
    
    db.commit()
    db.refresh(commission)
    return commission


def delete_commission(db: Session, commission_id):
    commission = get_commission_by_id(db, commission_id)
    if commission:
        db.delete(commission)
        db.commit()
        return True
    return False

# Transaction Overview returns total commissions and breakdown by status for ALL salespersons
def get_commission_overview(db: Session):
    status_summary = (
        db.query(
            models.CommissionRecord.status,
            func.sum(models.CommissionRecord.amount).label("total_amount"),
            func.count(models.CommissionRecord.id).label("count")
        )
        .group_by(models.CommissionRecord.status)
        .all()
    )

    total_commissions = db.query(func.count(models.CommissionRecord.id)).scalar() or 0
    total_amount = db.query(func.sum(models.CommissionRecord.amount)).scalar() or 0

    # Return a safe empty summary if no commissions exist
    if total_commissions == 0:
        return {
            "overall": {"total_commissions": 0, "total_amount": 0},
            "by_status": []
        }

    return {
        "overall": {"total_commissions": total_commissions, "total_amount": total_amount},
        "by_status": [
            {
                "status": str(s.status.value if hasattr(s.status, "value") else s.status),
                "count": s.count,
                "total_amount": s.total_amount or 0
            }
            for s in status_summary
        ]
    }


# Salesperson Transaction Summary returns total commissions and breakdown by status for a SPECIFIC salesperson
def get_commission_summary_by_salesperson(db: Session, salesperson_id):
    results = (
        db.query(
            models.CommissionRecord.status,
            func.sum(models.CommissionRecord.amount).label("total_amount"),
            func.count(models.CommissionRecord.id).label("count")
        )
        .filter(models.CommissionRecord.salesperson_id == salesperson_id)
        .group_by(models.CommissionRecord.status)
        .all()
    )

    # Compute overall totals
    total_amount = db.query(func.sum(models.CommissionRecord.amount)).filter(
        models.CommissionRecord.salesperson_id == salesperson_id
    ).scalar() or 0

    total_count = db.query(func.count(models.CommissionRecord.id)).filter(
        models.CommissionRecord.salesperson_id == salesperson_id
    ).scalar() or 0

    return {
        "salesperson_id": str(salesperson_id),
        "overall": {
            "total_commissions": total_count,
            "total_amount": total_amount
        },
        "by_status": [
            {
                "status": str(r.status.value if hasattr(r.status, "value") else r.status),
                "count": r.count,
                "total_amount": r.total_amount or 0
            }
            for r in results
        ]
    }