from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from apps.auth import models
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings
from core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    payload = {
        "sub": data.get("sub"),
        "is_admin": data.get("is_admin", False),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# User Authentication
oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_user_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    return user


# Admin Authentication
oauth2_admin_scheme = OAuth2PasswordBearer(
    tokenUrl="/admin/login",
    auto_error=False
)


def get_current_admin(token: str = Depends(oauth2_admin_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing admin token")

    payload = decode_access_token(token)

    if not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )

    return payload
