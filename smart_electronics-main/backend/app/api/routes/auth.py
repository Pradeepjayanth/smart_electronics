"""
Auth Routes
============

Endpoints for user registration, login, password change,
and forgot password functionality.

Routes:
    POST /auth/register     — Register a new user
    POST /auth/login        — Login and receive JWT tokens
    POST /auth/change-password — Change password (authenticated)
    POST /auth/forgot-password — Request password reset (placeholder)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.database.mongodb import get_db
from app.schemas.user import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with the specified role.",
)
async def register(
    request: UserRegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Register a new user account.

    Validates uniqueness of email and username, hashes the password,
    stores the user in MongoDB, and returns JWT tokens.
    """
    service = AuthService(db)
    try:
        result = await service.register(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password to receive JWT tokens.",
)
async def login(
    request: UserLoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Authenticate a user and return JWT access and refresh tokens.
    """
    service = AuthService(db)
    try:
        result = await service.login(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/change-password",
    summary="Change password",
    description="Change the password for the currently authenticated user.",
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Change the authenticated user's password.

    Requires the current password for verification.
    """
    service = AuthService(db)
    try:
        result = await service.change_password(
            user_id=current_user["_id"],
            current_password=request.current_password,
            new_password=request.new_password,
        )
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/forgot-password",
    summary="Forgot password",
    description="Request a password reset email (placeholder).",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Request a password reset.

    This is a placeholder endpoint. In production, it would
    send a password reset email with a time-limited token.
    Always returns success to prevent email enumeration.
    """
    service = AuthService(db)
    result = await service.forgot_password(request.email)
    return {"success": True, **result}
