"""
API Dependencies
=================

FastAPI dependency injection functions used across all route handlers.
Provides database access and authenticated user extraction from JWT tokens.

Usage in routes:
    @router.get("/protected")
    async def protected_route(
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        ...
"""

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import decode_access_token
from app.database.mongodb import get_db
from app.utils.logger import logger

# HTTP Bearer token extractor for Authorization header
security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    """
    Extract and validate the current user from the JWT bearer token.

    This dependency:
    1. Extracts the token from the Authorization header.
    2. Decodes and validates the JWT.
    3. Fetches the user from MongoDB.
    4. Verifies the account is active.

    Args:
        credentials: The bearer token from the Authorization header.
        db: The MongoDB database instance.

    Returns:
        The authenticated user document (with _id as string).

    Raises:
        HTTPException (401): If token is invalid, expired, or user not found.
        HTTPException (403): If user account is deactivated.
    """
    token = credentials.credentials

    # Decode the JWT
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token subject
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    # Convert ObjectId to string for convenience in downstream code
    user["_id"] = str(user["_id"])
    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Convenience dependency that ensures the current user is active.

    This is redundant with get_current_user's check but provides
    a semantic alias for routes that want to be explicit.

    Args:
        current_user: The authenticated user from get_current_user.

    Returns:
        The verified active user dict.
    """
    return current_user


def require_roles(*allowed_roles: str):
    """
    Create a dependency that enforces role-based access control.

    This is the production implementation that replaces the placeholder
    in app.core.permissions. It uses get_current_user to resolve the
    authenticated user and checks their role.

    Args:
        *allowed_roles: Role strings that are permitted access.

    Returns:
        A FastAPI dependency function.

    Usage:
        @router.delete("/item", dependencies=[Depends(require_roles("admin"))])
        async def delete_item():
            ...
    """

    async def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_role = current_user.get("role", "")
        if user_role not in allowed_roles:
            logger.warning(
                f"RBAC denied: user={current_user.get('email')} "
                f"role={user_role} required={allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker
