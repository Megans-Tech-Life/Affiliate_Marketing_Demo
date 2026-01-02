from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

# Enums for withdrawal status, transaction type, and payout method
class WithdrawalStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"

class TransactionType(str, Enum):
    COMMISSION_CREDIT = "commission_credit"
    WITHDRAWAL_REQUESTED = "withdrawal_requested"
    WITHDRAWAL_COMPLETED = "withdrawal_completed"
    WITHDRAWAL_REJECTED = "withdrawal_rejected"
    ADJUSTMENT_CREDIT = "adjustment_credit"
    ADJUSTMENT_DEBIT = "adjustment_debit"

class PayoutMethod(str, Enum):
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class WalletResponse(BaseModel):
    id: UUID
    person_id: UUID
    currency: str
    available_balance: Decimal
    pending_payout_amount: Decimal
    lifetime_earnings: Decimal
    lifetime_withdrawals: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletTransactionResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    type: TransactionType
    amount: Decimal
    balance_after: Decimal
    related_withdrawal_id: Optional[UUID]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WithdrawalRequestCreate(BaseModel):
    amount: Decimal
    payout_method: PayoutMethod

    # Only required for bank transfers
    bank_account_holder_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_ifsc_code: Optional[str] = None

    # Only required for PayPal
    paypal_email: Optional[str] = None


class WithdrawalStatusUpdate(BaseModel):
    status: WithdrawalStatus
    admin_comments: Optional[str] = None


class WithdrawalRequestResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    requested_by_id: UUID
    amount: Decimal
    currency: str
    status: WithdrawalStatus
    payout_method: PayoutMethod
    bank_account_holder_name: Optional[str]
    bank_account_number: Optional[str]
    bank_name: Optional[str]
    bank_ifsc_code: Optional[str]
    paypal_email: Optional[str]
    admin_comments: Optional[str]
    reference_id: Optional[str]
    requested_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class CommissionCredit(BaseModel):
    amount: Decimal = Field(..., gt=0)
