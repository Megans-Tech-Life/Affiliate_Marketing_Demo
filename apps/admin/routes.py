from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from apps.admin import models, services
from apps.admin.schemas import AdminLoginRequest, TokenResponse, AdminAccountResponse
from sqlalchemy.orm import Session
from apps.auth.security import get_current_admin, get_current_user
from apps.auth import schemas
from apps.auth.models import User
from core.database import get_db
from apps.admin.services import (
    verify_admin_credentials,
    rehash_admin_hash_if_needed,
    create_access_token,
)
from .dashboard_routes import router as dashboard_router

router = APIRouter(prefix="/admin", tags=["Admin"])
router.include_router(dashboard_router)

# Admin login route to authenticate and issue JWT
@router.post("/login", response_model=TokenResponse, summary="Authenticate admin and issue JWT")
def admin_login(body: AdminLoginRequest):
    ok = verify_admin_credentials(body.admin_id, body.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )

    # Rehash the admin's password for extra security
    rehash_admin_hash_if_needed(body.password)

    # Generate a JWT for the admin
    token, expires_in = create_access_token(subject=body.admin_id)

    return TokenResponse(access_token=token, expires_in=expires_in)

# Get all accounts
@router.get("/accounts", response_model=List[AdminAccountResponse])
def get_all_accounts(db: Session = Depends(get_db),
                     current_admin = Depends(get_current_admin)):
    return services.get_all_accounts(db)

# Get all users
# @router.get("/users", response_model=list[schemas.UserResponse])
# def get_all_users(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     if not current_user.is_superuser:
#         raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(models.User).all()
