"""
Authentication Service
=======================

Business logic for user registration, login, token management,
and password operations. Separated from route handlers for testability
and adherence to the Single Responsibility Principle.
"""

from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.config import get_settings
from app.models.user import create_user_document
from app.schemas.user import UserRegisterRequest, UserLoginRequest
from app.utils.logger import logger


class AuthService:
    """
    Handles authentication-related business logic.

    All database operations go through the injected db instance,
    making this service easy to test with a mock database.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def register(self, request: UserRegisterRequest) -> dict:
        """
        Register a new user.

        Validates uniqueness of email and username, hashes the password,
        creates the user document, and returns user data with tokens.

        Args:
            request: Validated registration data.

        Returns:
            Dict containing user data and JWT tokens.

        Raises:
            ValueError: If email or username already exists.
        """
        # Check for existing email
        existing_email = await self.collection.find_one({"email": request.email})
        if existing_email:
            raise ValueError("A user with this email already exists.")

        # Check for existing username
        existing_username = await self.collection.find_one(
            {"username": request.username}
        )
        if existing_username:
            raise ValueError("A user with this username already exists.")

        # Create user document with hashed password
        hashed = hash_password(request.password)
        user_doc = create_user_document(
            username=request.username,
            email=request.email,
            hashed_password=hashed,
            full_name=request.full_name,
            role=request.role,
            phone=request.phone,
            department=request.department,
        )

        # Insert into MongoDB
        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        logger.info(f"User registered: {request.email} (role: {request.role})")

        # Generate tokens
        token_data = {"sub": str(result.inserted_id), "role": user_doc["role"]}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        settings = get_settings()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": self._format_user(user_doc),
        }

    async def login(self, request: UserLoginRequest) -> dict:
        """
        Authenticate a user and return JWT tokens.

        Args:
            request: Validated login credentials.

        Returns:
            Dict containing user data and JWT tokens.

        Raises:
            ValueError: If credentials are invalid or account is inactive.
        """
        # Find user by email
        user = await self.collection.find_one({"email": request.email})
        if not user:
            raise ValueError("Invalid email or password.")

        # Verify password
        if not verify_password(request.password, user["hashed_password"]):
            raise ValueError("Invalid email or password.")

        # Check if account is active
        if not user.get("is_active", True):
            raise ValueError("Account is deactivated. Contact an administrator.")

        # Update last login timestamp
        await self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}},
        )

        logger.info(f"User logged in: {request.email}")

        # Generate tokens
        token_data = {"sub": str(user["_id"]), "role": user["role"]}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        settings = get_settings()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": self._format_user(user),
        }

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> dict:
        """
        Change the password for an authenticated user.

        Args:
            user_id: The authenticated user's ID.
            current_password: The user's current password.
            new_password: The new password to set.

        Returns:
            Success message dict.

        Raises:
            ValueError: If current password is incorrect or user not found.
        """
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found.")

        if not verify_password(current_password, user["hashed_password"]):
            raise ValueError("Current password is incorrect.")

        # Hash and update the new password
        new_hashed = hash_password(new_password)
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "hashed_password": new_hashed,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        logger.info(f"Password changed for user: {user['email']}")
        return {"message": "Password changed successfully."}

    async def forgot_password(self, email: str) -> dict:
        """
        Placeholder for forgot password functionality.

        In production, this would send a password reset email.
        Currently returns a success message regardless of whether
        the email exists (to prevent email enumeration attacks).

        Args:
            email: The email address to send reset instructions to.

        Returns:
            Success message dict.
        """
        # Check if user exists (log only, don't reveal to client)
        user = await self.collection.find_one({"email": email})
        if user:
            logger.info(f"Password reset requested for: {email}")
            # TODO: Send password reset email with token
        else:
            logger.info(f"Password reset requested for non-existent email: {email}")

        # Always return success to prevent email enumeration
        return {
            "message": "If an account with this email exists, "
                       "a password reset link has been sent."
        }

    @staticmethod
    def _format_user(user: dict) -> dict:
        """
        Format a MongoDB user document for API response.

        Removes sensitive fields (password) and converts ObjectId to string.

        Args:
            user: Raw MongoDB user document.

        Returns:
            Sanitized user dict for API response.
        """
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "role": user["role"],
            "phone": user.get("phone", ""),
            "department": user.get("department", ""),
            "is_active": user.get("is_active", True),
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "last_login": user.get("last_login"),
        }
