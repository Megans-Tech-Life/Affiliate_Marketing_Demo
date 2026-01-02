from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from apps.auth.security import get_current_user
from apps.contacts.models import PersonOfContact
from apps.wallet.models import Wallet
from . import schemas, models, security

from core.database import get_db
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# User Registration
@router.post(
    "/register",
    response_model=schemas.LoginResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Prevent duplicate email
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user_data.email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = security.hash_password(user_data.password)

    # Create User record
    new_user = models.User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_code=user_data.phone_code,
        phone_no=user_data.phone_no,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create matching PERSON record 
    new_person = PersonOfContact(
        user_id=new_user.id,
        role=None,
        personality_type=None
    )

    db.add(new_person)
    db.commit()
    db.refresh(new_person)

    # Create wallet immediately after user registration
    wallet = Wallet(
        person_id=new_person.id,
        available_balance=0.00,
        currency="USD",
        pending_payout_amount=0.00,
        lifetime_earnings=0.00,
        lifetime_withdrawals=0.00,
        is_active=True,
        is_deleted=False
    )

    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

# User Login
@router.post("/login", response_model=schemas.LoginResponse)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password")
    
    # Verify password
    if not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password")
    
    # Create JWT token with expiration
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )

    # Return the token
    return {"access_token": access_token, 
            "token_type": "bearer",
            "user": user}

@router.post("/check-email", response_model=schemas.CheckEmailResponse)
def check_email_exists(payload: schemas.CheckEmailRequest, db: Session = Depends(get_db)):
    exists = ( db.query(models.User)
              .filter(models.User.email == payload.email)
              .first() is not None
              )
    return {"exists": exists}

# Get current user
@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user

