"""
Authentication utilities for Resync admin endpoints.
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from resync.settings import settings

# Security schemes
# Allow missing Authorization to support HttpOnly cookie fallback
security = HTTPBearer(auto_error=False)

# Secret key for JWT tokens
SECRET_KEY = getattr(settings, "SECRET_KEY", "fallback_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_admin_credentials(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Verify admin credentials for protected endpoints using JWT tokens.
    """
    try:
        # 1) Try Authorization header (Bearer)
        token = credentials.credentials if (credentials and credentials.credentials) else None

        # 2) Fallback: HttpOnly cookie "access_token"
        if not token:
            token = request.cookies.get("access_token")
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credentials not provided",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Decode & validate JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Accept ADMIN_USERNAME or admin_username for compatibility
        admin_user = getattr(settings, "ADMIN_USERNAME", None) or getattr(settings, "admin_username", None)
        if username != admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_admin(username: str, password: str):
    """
    Authenticate admin user credentials with enhanced security validation.
    """
    # Verify the username matches the admin username from settings
    admin_user = getattr(settings, "ADMIN_USERNAME", None) or getattr(settings, "admin_username", None)
    if username != admin_user:
        return False

    try:
        from resync.api.validation.enhanced_security_fixed import EnhancedSecurityValidator
        validator = EnhancedSecurityValidator()
        stored_hash = await validator.hash_password(getattr(settings, "ADMIN_PASSWORD", getattr(settings, "admin_password", "")))
        is_valid = await validator.verify_password(password, stored_hash)
        return is_valid
    except Exception:
        # Fallback to simple comparison for compatibility
        return password == (getattr(settings, "ADMIN_PASSWORD", None) or getattr(settings, "admin_password", ""))

    return False
