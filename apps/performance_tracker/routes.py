from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from . import services

router = APIRouter(prefix="/performance", tags=["Performance Tracker"])

# Get performance analytics for a specific salesperson
@router.get("/salesperson/{salesperson_id}")
def get_salesperson_performance(salesperson_id: str, db: Session = Depends(get_db)):
    performance = services.calculate_salesperson_performance(db, salesperson_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Salesperson not found")
    return performance

# Suggest salespersons based on client personality type
@router.get("/personality-match/{client_personality}")
def personality_match(client_personality: str, db: Session = Depends(get_db)):
  suggestions = services.personality_match(db, client_personality)
  return suggestions