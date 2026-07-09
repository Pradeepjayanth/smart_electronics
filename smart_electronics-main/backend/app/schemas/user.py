"""
User Schemas
=============

Pydantic schemas for user registration, login, profile,
and password management endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Schema for user registration."""
    username: str = Field(
        ..., min_length=3, max_length=50,
        description="Unique username (3-50 characters)",
    )
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(
        ..., min_length=8, max_length=128,
        description="Password (8-128 characters)",
    )
    full_name: str = Field(
        default="", max_length=100, description="User's full name",
    )
    role: str = Field(
        default="customer",
        description="User role: admin, engineer, technician, customer",
    )
    phone: str = Field(default="", max_length=20, description="Phone number")
    department: str = Field(default="", max_length=100, description="Department")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is one of the allowed values."""
        allowed = {"admin", "engineer", "technician", "customer"}
        if v.lower() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Ensure username contains only alphanumeric characters and underscores."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username must contain only letters, numbers, hyphens, and underscores"
            )
        return v.lower()


class UserLoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")


class ChangePasswordRequest(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128,
        description="New password (8-128 characters)",
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Ensure new password meets complexity requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password (placeholder)."""
    email: EmailStr = Field(..., description="Registered email address")


class UserUpdateRequest(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    id: str = Field(..., description="User ID")
    username: str
    email: str
    full_name: str
    role: str
    phone: str
    department: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Schema for JWT token response after login."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user: UserResponse = Field(..., description="Authenticated user data")
