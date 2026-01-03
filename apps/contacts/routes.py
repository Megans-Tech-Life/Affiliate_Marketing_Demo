from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from apps.admin import models
from apps.auth.models import User
from apps.auth.security import get_current_user
from core.database import get_db
from . import schemas, services

router = APIRouter(prefix="/contacts", tags=["Contacts"])

# Create a new contact
@router.post("/", response_model=schemas.POCResponse)
def create_poc(poc: schemas.POCCreate, 
               db: Session = Depends(get_db), 
               current_user: User = Security(get_current_user)):
    return services.create_poc(db, poc, current_user)

# Get all contacts (active)
@router.get("/", response_model=list[schemas.POCResponse])
def get_all_pocs(db: Session = Depends(get_db)):
    return services.get_all_pocs(db)

# Get deleted contacts (trash)
@router.get("/trash", response_model=list[schemas.POCResponse])
def get_deleted_pocs(db: Session = Depends(get_db)):
    return services.get_deleted_pocs(db)

# Get a single contact by ID
@router.get("/{poc_id}", response_model=schemas.POCResponse)
def get_poc(poc_id: str, db: Session = Depends(get_db)):
   return services.get_poc_by_id(db, poc_id)

# Update contact
@router.put("/{poc_id}", response_model=schemas.POCResponse)
def update_poc(poc_id: str, poc_data: schemas.POCUpdate, db: Session = Depends(get_db)):
   return services.update_poc(db, poc_id, poc_data)

# Soft delete to trash
@router.delete("/{poc_id}")
def soft_delete_poc(poc_id: str, db: Session = Depends(get_db)):
   return services.soft_delete_poc(db, poc_id)

# Restore a contact from trash
@router.put("/restore/{poc_id}", response_model=schemas.POCResponse)
def restore_poc(poc_id: str, db: Session = Depends(get_db)):
   return services.restore_poc(db, poc_id)