import os
import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from apps.accounts.models import Account
from apps.admin.models import Admin
from core.config import settings

# Configuration from core settings
ADMIN_ID_ENV = os.getenv("ADMIN_ID", "superadmin")
ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "supersecretpassword")

# In-memory admin state starts as None
_admin_state: Optional[Admin] = None

# Hash a plaintext password using bcrypt
def _hash_password(plaintext: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plaintext.encode('utf-8'), salt).decode('utf-8')

# Initialize admin state if not loaded already
def _ensure_admin_loaded() -> Admin:
    global _admin_state
    if _admin_state is None:
        if not ADMIN_PASSWORD_ENV:
            raise ValueError("Admin password is not set in .env")
        HASHED = _hash_password(ADMIN_PASSWORD_ENV)
        _admin_state = Admin(admin_id=ADMIN_ID_ENV, hashed_password=HASHED)
    return _admin_state

# Verify admin credentials against stored admin data
def verify_admin_credentials(admin_id: str, password: str) -> bool:
    admin = _ensure_admin_loaded()
    if admin.admin_id != admin_id:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), admin.hashed_password.encode('utf-8'))
    except Exception:
        return False
    
# Rehashing admin password after login
def rehash_admin_hash_if_needed(plaintext_password: str) -> None:
    global _admin_state
    if plaintext_password:
        new_hash = _hash_password(plaintext_password)
        _admin_state = Admin(admin_id=ADMIN_ID_ENV, hashed_password=new_hash)

# Create JWT access token for admin
def create_access_token(subject: str, expires_minutes: int = None) -> Tuple[str, int]:
    if expires_minutes is None:
        expires_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)
    payload = {
        "sub": subject,
        "is_admin": True,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_minutes * 60 # Return values in seconds to frontend


# Get all accounts (active only) for admin view
def get_all_accounts(db: Session):
    return db.query(Account).filter(Account.is_deleted == False).all()
