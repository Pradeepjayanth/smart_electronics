"""
Role-Based Access Control (RBAC)
=================================

Provides a reusable FastAPI dependency for restricting route access
based on user roles. Supports four roles: Admin, Engineer, Technician, Customer.

Usage in routes:
    @router.get("/admin-only", dependencies=[Depends(require_roles("admin"))])
    async def admin_endpoint():
        ...

    @router.get("/multi-role", dependencies=[Depends(require_roles("admin", "engineer"))])
    async def multi_role_endpoint():
        ...
"""

from enum import Enum
from typing import List

from fastapi import Depends, HTTPException, status

from app.utils.logger import logger


class UserRole(str, Enum):
    """Enumeration of all supported user roles."""
    ADMIN = "admin"
    ENGINEER = "engineer"
    TECHNICIAN = "technician"
    CUSTOMER = "customer"


def require_roles(*allowed_roles: str):
    """
    Create a FastAPI dependency that enforces role-based access.

    This is a factory function that returns a dependency. The dependency
    checks whether the current user's role is in the list of allowed roles.

    Args:
        *allowed_roles: One or more role strings that are permitted access.

    Returns:
        A FastAPI dependency function.

    Raises:
        HTTPException (403): If the user's role is not in allowed_roles.
    """

    async def role_checker(current_user: dict = Depends(_get_current_user_for_rbac)):
        """
        Verify the current user has one of the allowed roles.

        Args:
            current_user: The authenticated user dict (injected via DI).

        Raises:
            HTTPException: 403 if the user's role is not permitted.
        """
        user_role = current_user.get("role", "")

        if user_role not in allowed_roles:
            logger.warning(
                f"Access denied for user {current_user.get('email')} "
                f"with role '{user_role}'. Required: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )

        return current_user

    return role_checker


async def _get_current_user_for_rbac():
    """
    Placeholder dependency for circular import avoidance.

    The actual get_current_user dependency is defined in app.api.deps.
    This function is overridden at application startup in main.py
    by replacing it with the real dependency via app.dependency_overrides.

    In practice, require_roles() is used alongside Depends(get_current_user)
    in routes, so the current_user is already resolved.
    """
    # This will be overridden — see app/api/deps.py
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication dependency not configured.",
    )


def get_all_roles() -> List[str]:
    """Return a list of all valid role values."""
    return [role.value for role in UserRole]
