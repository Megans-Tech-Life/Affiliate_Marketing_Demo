from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal

from apps.wallet.models import (
    Wallet,
    WalletTransaction,
    WithdrawalRequest,
    WithdrawalStatus,
    TransactionType,
)
from apps.contacts.models import PersonOfContact
from apps.wallet.schemas import (
    WithdrawalRequestCreate,
    WithdrawalStatusUpdate,
    CommissionCredit,
)
from fastapi import HTTPException, status


# Get or Create Wallet for User
def get_or_create_wallet(db: Session, user_id: UUID) -> Wallet:   
    # Find the POC linked to this user
    poc = (
        db.query(PersonOfContact)
        .filter(
            PersonOfContact.user_id == user_id,
            PersonOfContact.is_deleted == False
        )
        .first()
    )

    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No PersonOfContact found for this user.",
        )

    # Check if wallet already exists
    wallet = (
        db.query(Wallet)
        .filter(Wallet.person_id == poc.id, 
                Wallet.is_deleted == False)
        .first()
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for this user."
        )
    return wallet


# Admin: Credit Commission
def credit_commission(db: Session, person_id: UUID, data: CommissionCredit) -> Wallet:   
    wallet = (
        db.query(Wallet)
        .filter(Wallet.person_id == person_id, 
                Wallet.is_deleted == False)
        .first()
    )
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet does not exist for this person.",
        )

    amount = Decimal(str(data.amount))

    # Update wallet balances
    wallet.available_balance += amount
    wallet.lifetime_earnings += amount
    wallet.updated_at = datetime.now(timezone.utc)

    # Log transaction
    tx = WalletTransaction(
        wallet_id=wallet.id,
        type=TransactionType.COMMISSION_CREDIT,
        amount=amount,
        balance_after=wallet.available_balance,
        description=f"Commission credited: {amount}",
    )

    db.add(tx)
    db.commit()
    db.refresh(wallet)

    return wallet


# User: Request Withdrawal
def request_withdrawal(
    db: Session,
    user_id: UUID,
    data: WithdrawalRequestCreate
) -> WithdrawalRequest:

    # Ensure logged-in user has a POC record
    poc = (
        db.query(PersonOfContact)
        .filter(PersonOfContact.user_id == user_id, 
                PersonOfContact.is_deleted == False)
        .first()
    )
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PersonOfContact not found for this user."
        )

    # Get or create wallet
    wallet = db.query(Wallet).filter(
        Wallet.person_id == poc.id,
        Wallet.is_deleted == False
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for this user.(no commission earned yet)"
        )

    amount = Decimal(str(data.amount))

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal amount must be greater than 0."
        )

    if wallet.available_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient available balance."
        )

    # Deduct from available and move to pending
    wallet.available_balance -= amount
    wallet.pending_payout_amount += amount
    wallet.updated_at = datetime.now(timezone.utc)

    # Create withdrawal request
    withdrawal = WithdrawalRequest(
        wallet_id=wallet.id,
        requested_by_id=poc.id,
        amount=amount,
        currency=wallet.currency,
        payout_method=data.payout_method,
        bank_account_holder_name=data.bank_account_holder_name,
        bank_account_number=data.bank_account_number,
        bank_name=data.bank_name,
        bank_ifsc_code=data.bank_ifsc_code,
        paypal_email=data.paypal_email,
        status=WithdrawalStatus.REQUESTED,
    )

    db.add(withdrawal)

    # Log transaction
    tx = WalletTransaction(
        wallet_id=wallet.id,
        type=TransactionType.WITHDRAWAL_REQUESTED,
        amount=amount,
        balance_after=wallet.available_balance,
        related_withdrawal_id=withdrawal.id,
        description="Withdrawal requested"
    )

    db.add(tx)
    db.commit()
    db.refresh(withdrawal)

    return withdrawal


# Admin: Update Withdrawal Status
def update_withdrawal_status(
    db: Session,
    withdrawal_id: UUID,
    data: WithdrawalStatusUpdate
) -> WithdrawalRequest:

    withdrawal = (
        db.query(WithdrawalRequest)
        .filter(
            WithdrawalRequest.id == withdrawal_id,
            WithdrawalRequest.is_deleted == False
        )
        .first()
    )

    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal request not found."
        )

    wallet = withdrawal.wallet

    new_status = data.status

    # Handle status transitions
    if new_status == WithdrawalStatus.APPROVED:
        withdrawal.status = WithdrawalStatus.APPROVED

    elif new_status == WithdrawalStatus.COMPLETED:
        withdrawal.status = WithdrawalStatus.COMPLETED
        withdrawal.completed_at = datetime.now(timezone.utc)

        amount = withdrawal.amount

        wallet.pending_payout_amount -= amount
        wallet.lifetime_withdrawals += amount
        wallet.updated_at = datetime.now(timezone.utc)

        # Log completion transaction
        tx = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.WITHDRAWAL_COMPLETED,
            amount=amount,
            balance_after=wallet.available_balance,
            related_withdrawal_id=withdrawal.id,
            description="Withdrawal completed"
        )
        db.add(tx)

    elif new_status == WithdrawalStatus.REJECTED:
        withdrawal.status = WithdrawalStatus.REJECTED

        # Return funds to available balance
        wallet.available_balance += withdrawal.amount
        wallet.pending_payout_amount -= withdrawal.amount

        tx = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.WITHDRAWAL_REJECTED,
            amount=withdrawal.amount,
            balance_after=wallet.available_balance,
            related_withdrawal_id=withdrawal.id,
            description="Withdrawal rejected"
        )
        db.add(tx)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid withdrawal status."
        )

    db.commit()
    db.refresh(withdrawal)
    return withdrawal
