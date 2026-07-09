"""
Security Module
================

Provides JWT token management and password hashing utilities.
- JWT: HS256-based access tokens with configurable expiry.
- Passwords: bcrypt hashing with automatic salt generation.

All security operations are centralized here to ensure consistency
and make it easy to audit or swap algorithms in the future.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.utils.logger import logger

# Password hashing context — bcrypt with automatic salt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: The plaintext password to hash.

    Returns:
        The bcrypt-hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: The plaintext password to check.
        hashed_password: The stored bcrypt hash to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.

    Encodes the provided data into a JWT with an expiration claim.
    The token is signed with HS256 using the configured secret key.

    Args:
        data: The payload to encode (must include "sub" for subject).
        expires_delta: Optional custom expiration duration.
            Defaults to JWT_ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    Returns:
        The encoded JWT token string.
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    logger.debug(f"Access token created for subject: {data.get('sub')}")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with a longer expiration.

    Args:
        data: The payload to encode (must include "sub" for subject).

    Returns:
        The encoded JWT refresh token string.
    """
    settings = get_settings()
    expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    })

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify a JWT access token.

    Validates the token signature and expiration. Returns the decoded
    payload if valid, or None if the token is invalid or expired.

    Args:
        token: The JWT token string to decode.

    Returns:
        The decoded payload dict if valid, None otherwise.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode failed: {e}")
        return None
