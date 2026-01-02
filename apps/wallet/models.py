import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class WithdrawalStatus(str, PyEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"

class PayoutMethod(str, PyEnum):
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class TransactionType(str, PyEnum):
    COMMISSION_CREDIT = "commission_credit"
    WITHDRAWAL_REQUESTED = "withdrawal_requested"
    WITHDRAWAL_COMPLETED = "withdrawal_completed"
    WITHDRAWAL_REJECTED = "withdrawal_rejected"
    ADJUSTMENT_CREDIT = "adjustment_credit"
    ADJUSTMENT_DEBIT = "adjustment_debit"

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False, index=True)

    currency = Column(String(10), nullable=False, default="USD")

    available_balance = Column(Numeric(12, 2), nullable=False, default=0.00)
    pending_payout_amount = Column(Numeric(12, 2), nullable=False, default=0.00)
    lifetime_earnings = Column(Numeric(12, 2), nullable=False, default=0.00)
    lifetime_withdrawals = Column(Numeric(12, 2), nullable=False, default=0.00)

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    person = relationship("PersonOfContact", back_populates="wallet", lazy="joined")
    transactions = relationship("WalletTransaction", back_populates="wallet")
    withdrawal_requests = relationship("WithdrawalRequest", back_populates="wallet")


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True)
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False, index=True)

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="USD")

    status = Column(Enum(WithdrawalStatus), name="withdrawal_status_enum",
                    default=WithdrawalStatus.REQUESTED, nullable=False, index=True)

    payout_method = Column(Enum(PayoutMethod), name="payout_method_enum", nullable=False)

    bank_account_holder_name = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_name = Column(String(255), nullable=True)
    bank_ifsc_code = Column(String(50), nullable=True)
    paypal_email = Column(String(255), nullable=True)

    admin_comments = Column(String(500), nullable=True)
    reference_id = Column(String(100), unique=True, nullable=True)

    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    is_deleted = Column(Boolean, default=False)

    # Relationships
    wallet = relationship("Wallet", back_populates="withdrawal_requests")
    requested_by = relationship("PersonOfContact", back_populates="withdrawal_requests", lazy="joined")
    transactions = relationship("WalletTransaction", back_populates="related_withdrawal")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True)
    
    type = Column(Enum(TransactionType), name="transaction_type_enum", nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    balance_after = Column(Numeric(12, 2), nullable=False)

    related_withdrawal_id = Column(UUID(as_uuid=True), ForeignKey("withdrawal_requests.id"),
                                   nullable=True, index=True)

    description = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    related_withdrawal = relationship("WithdrawalRequest", back_populates="transactions")
