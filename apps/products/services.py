from sqlalchemy.orm import Session
from fastapi import logger
from . import models, schemas
from apps.contacts.models import PersonOfContact

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        category=product.category,
        description=product.description,
        price_value=product.price_value
    )

    if product.persons_ids:
        db_product.persons = db.query(PersonOfContact).filter(PersonOfContact.id.in_(product.persons_ids)).all()

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_all_products(db: Session):
    return db.query(models.Product).filter(models.Product.is_deleted == False).all()

def get_product(db: Session, product_id: str):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: str, product_data: schemas.ProductUpdate):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return None

    update_data = product_data.model_dump(exclude_unset=True)
    unsupported_fields = []

    for key, value in update_data.items():
        if hasattr(db_product, key):
            setattr(db_product, key, value)
        else:
            unsupported_fields.append(key)
    
    if unsupported_fields:
        logger.warning(
            f"Unsupported fields received in product update: {unsupported_fields}"
        )

    db.commit()
    db.refresh(db_product)
    return db_product

def soft_delete_product(db: Session, product_id: str):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.is_deleted = True
        db.commit()
        db.refresh(product)
    return product

def get_deleted_products(db: Session):
    return db.query(models.Product).filter(models.Product.is_deleted == True).all()

def restore_product(db: Session, product_id: str):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.is_deleted = False
        db.commit()
        db.refresh(product)
    return product
