"""
User Document Model
====================

Defines the structure for documents in the 'users' MongoDB collection.
Supports roles: admin, engineer, technician, customer.
"""

from datetime import datetime, timezone


def create_user_document(
    username: str,
    email: str,
    hashed_password: str,
    full_name: str = "",
    role: str = "customer",
    phone: str = "",
    department: str = "",
) -> dict:
    """
    Create a new user document for MongoDB insertion.

    Args:
        username: Unique username.
        email: Unique email address.
        hashed_password: Bcrypt-hashed password.
        full_name: User's full name.
        role: User role (admin, engineer, technician, customer).
        phone: Contact phone number.
        department: Department or team.

    Returns:
        A dict representing the user document.
    """
    now = datetime.now(timezone.utc)
    return {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "role": role,
        "phone": phone,
        "department": department,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login": None,
    }
