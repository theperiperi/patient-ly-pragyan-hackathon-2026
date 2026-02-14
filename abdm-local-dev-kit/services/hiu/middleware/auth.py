import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


class TokenData(BaseModel):
    """Token data model."""
    sub: str
    exp: datetime
    scope: Optional[list] = []


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration delta (defaults to access_token_expire_minutes)

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> TokenData:
    """
    Verify JWT token from Authorization header.

    Args:
        credentials: HTTP bearer credentials

    Returns:
        Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.algorithm]
        )
        sub: str = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        token_data = TokenData(
            sub=sub,
            exp=datetime.fromtimestamp(payload.get("exp")),
            scope=payload.get("scope", [])
        )
        return token_data
    except JWTError as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user(token: TokenData = Depends(verify_token)) -> str:
    """
    Get current authenticated user from token.

    Args:
        token: Token data from JWT verification

    Returns:
        User subject (ID) from token
    """
    return token.sub


async def optional_token(
    credentials: Optional[HTTPAuthCredentials] = Depends(security)
) -> Optional[TokenData]:
    """
    Optional token verification - returns None if no token provided.

    Args:
        credentials: Optional HTTP bearer credentials

    Returns:
        Token data if token provided and valid, None otherwise
    """
    if not credentials:
        return None
    return verify_token(credentials)
