from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from . import schemas, services

router = APIRouter(prefix="/products", tags=["Products"])

# Create a new Product
@router.post("/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return services.create_product(db, product)

# Get all Products
@router.get("/", response_model=list[schemas.ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    return services.get_all_products(db)

# Get deleted Products
@router.get("/trash", response_model=list[schemas.ProductResponse])
def get_deleted_products(db: Session = Depends(get_db)):
    return services.get_deleted_products(db)

# Get, Update, Delete a Product by ID
@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    db_product = services.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: UUID, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated_product = services.update_product(db, product_id, product_update)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    db_product = services.soft_delete_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product moved to trash successfully"}

# Restore a Product from trash
@router.put("/restore/{product_id}", response_model=schemas.ProductResponse)
def restore_product(product_id: UUID, db: Session = Depends(get_db)):
    restored_product = services.restore_product(db, product_id)
    if not restored_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return restored_product