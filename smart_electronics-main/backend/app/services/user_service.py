"""
User Service
=============

Business logic for user profile management and admin user operations.
"""

from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.logger import logger


class UserService:
    """
    Handles user profile and management operations.

    Separated from AuthService to follow Single Responsibility Principle:
    AuthService handles authentication, UserService handles user data.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def get_profile(self, user_id: str) -> dict:
        """
        Get user profile by ID.

        Args:
            user_id: The user's MongoDB ObjectId string.

        Returns:
            Formatted user profile dict.

        Raises:
            ValueError: If user not found.
        """
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found.")
        return self._format_user(user)

    async def update_profile(self, user_id: str, update_data: dict) -> dict:
        """
        Update user profile fields.

        Only updates provided (non-None) fields to support partial updates.

        Args:
            user_id: The user's MongoDB ObjectId string.
            update_data: Dict of fields to update.

        Returns:
            Updated user profile dict.

        Raises:
            ValueError: If user not found.
        """
        # Filter out None values for partial update
        updates = {k: v for k, v in update_data.items() if v is not None}
        if not updates:
            raise ValueError("No fields to update.")

        updates["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates},
        )

        if result.matched_count == 0:
            raise ValueError("User not found.")

        logger.info(f"Profile updated for user: {user_id}")
        return await self.get_profile(user_id)

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: str | None = None,
    ) -> dict:
        """
        List all users with pagination (admin only).

        Args:
            page: Page number (1-indexed).
            page_size: Number of users per page.
            role: Optional filter by role.

        Returns:
            Dict with paginated users list and total count.
        """
        query = {}
        if role:
            query["role"] = role

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = self.collection.find(query).skip(skip).limit(page_size).sort(
            "created_at", -1
        )

        users = []
        async for user in cursor:
            users.append(self._format_user(user))

        return {
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_user_by_id(self, user_id: str) -> dict | None:
        """
        Get a raw user document by ID (internal use).

        Args:
            user_id: The user's MongoDB ObjectId string.

        Returns:
            Raw user document or None if not found.
        """
        try:
            return await self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    @staticmethod
    def _format_user(user: dict) -> dict:
        """
        Format a MongoDB user document for API response.

        Strips sensitive fields and converts ObjectId.
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
