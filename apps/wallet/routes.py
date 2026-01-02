from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from core.database import get_db
from apps.auth.security import get_current_admin, get_current_user
from apps.contacts.models import PersonOfContact
from .services import (
    get_or_create_wallet,
    credit_commission,
    request_withdrawal,
    update_withdrawal_status,
)
from .schemas import (
    WalletResponse,
    WalletTransactionResponse,
    WithdrawalRequestCreate,
    WithdrawalStatusUpdate,
    WithdrawalRequestResponse,
    CommissionCredit,
)
from .models import Wallet, WalletTransaction, WithdrawalRequest


router = APIRouter(prefix="/wallet", tags=["Wallet"])


# Get wallet for logged-in user
@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    wallet = get_or_create_wallet(db, current_user.id)
    return wallet


# Admin: Credit commission to a POC wallet
@router.post("/commission/{person_id}", response_model=WalletResponse)
def add_commission(
    person_id: UUID,
    data: CommissionCredit,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    wallet = credit_commission(db, person_id, data)
    return wallet


# User: Request withdrawal
@router.post("/withdrawals", response_model=WithdrawalRequestResponse)
def request_withdrawal_route(
    data: WithdrawalRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    withdrawal = request_withdrawal(db, current_user.id, data)
    return withdrawal


# User: View own withdrawal requests
@router.get("/withdrawals/me", response_model=list[WithdrawalRequestResponse])
def get_my_withdrawals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    poc = db.query(PersonOfContact).filter(
        PersonOfContact.user_id == current_user.id,
        PersonOfContact.is_deleted == False
    ).first()

    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PersonOfContact not found for this user."
        )

    records = (
        db.query(WithdrawalRequest)
        .filter(
            WithdrawalRequest.requested_by_id == poc.id,
            WithdrawalRequest.is_deleted == False
        )
        .order_by(WithdrawalRequest.requested_at.desc())
        .all()
    )

    return records


# Admin: Update withdrawal status
@router.put("/withdrawals/{withdrawal_id}", response_model=WithdrawalRequestResponse)
def admin_update_withdrawal_status(
    withdrawal_id: UUID,
    data: WithdrawalStatusUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    updated = update_withdrawal_status(db, withdrawal_id, data)
    return updated


# Admin: Get transaction log for a person (by person_id)
@router.get("/{person_id}/transactions", response_model=list[WalletTransactionResponse])
def get_transaction_log(
    person_id: UUID,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):

    wallet = db.query(Wallet).filter(
        Wallet.person_id == person_id,
        Wallet.is_deleted == False
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for this person."
        )

    tx_list = (
        db.query(WalletTransaction)
        .filter(
            WalletTransaction.wallet_id == wallet.id,
            WalletTransaction.is_deleted == False
        )
        .order_by(WalletTransaction.created_at.desc())
        .all()
    )

    return tx_list
