from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List

class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    price_value: Optional[dict] = None  # Example {"base_price": 1000.0, "estimated_price": 1200.0}

class ProductCreate(ProductBase):
    persons_ids: Optional[List[UUID]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price_value: Optional[dict] = None  # Example {"base_price": 1000.0, "estimated_price": 1200.0}
    persons_ids: Optional[List[UUID]] = []

class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True
