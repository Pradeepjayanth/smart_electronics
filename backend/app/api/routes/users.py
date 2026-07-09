"""
User Routes
============

Endpoints for user profile management and admin user operations.

Routes:
    GET  /users/me     — Get current user's profile
    PUT  /users/me     — Update current user's profile
    GET  /users        — List all users (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, require_roles
from app.database.mongodb import get_db
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get my profile",
    description="Retrieve the authenticated user's profile data.",
)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get the current authenticated user's profile."""
    service = UserService(db)
    try:
        return await service.get_profile(current_user["_id"])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update my profile",
    description="Update the authenticated user's profile fields.",
)
async def update_my_profile(
    request: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update the current authenticated user's profile."""
    service = UserService(db)
    try:
        return await service.update_profile(
            user_id=current_user["_id"],
            update_data=request.model_dump(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    summary="List all users",
    description="List all users with pagination. Admin only.",
    dependencies=[Depends(require_roles("admin"))],
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: str | None = Query(None, description="Filter by role"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List all users (admin access required)."""
    service = UserService(db)
    return await service.list_users(page=page, page_size=page_size, role=role)
