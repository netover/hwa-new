from __future__ import annotations
from pydantic import BaseModel, EmailStr, validator, Field
from pydantic.network import EmailStr
from typing import Optional
from passlib.context import CryptContext

# --- Password Validation Context ---
password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, example="johndoe")
    password: str = Field(..., min_length=8, example="securepassword123!")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, example="johndoe")
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="securepassword123!")

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime

class TokenRequest(BaseModel):
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

class OAuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int