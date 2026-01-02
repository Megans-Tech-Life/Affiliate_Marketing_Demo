import uuid
from datetime import datetime, timezone
from sqlalchemy import JSON, Boolean, Column, String, Float, DateTime, Table, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

# Association table between Products and Persons of Contact
product_persons = Table(
    "product_persons",
    Base.metadata,
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id")),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id"))
)

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
   
    # Pricing information
    price_value = Column(JSON, nullable=True) 

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    is_deleted = Column(Boolean, default=False)

    # Relationships
    persons = relationship(
        "PersonOfContact",
        secondary=product_persons,
        back_populates="products"
    )

    opportunities = relationship(
        "Opportunity",
        secondary="opportunity_products",
        back_populates="products",
        lazy="joined"
    )

