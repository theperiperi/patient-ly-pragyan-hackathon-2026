"""
JWT authentication middleware for securing API endpoints.
Validates JWT tokens from Authorization header.
"""

import logging
from typing import Callable, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT token validation.
    Validates tokens in Authorization header for protected routes.
    """

    def __init__(self, app, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize the JWT middleware.

        Args:
            app: The FastAPI application
            secret_key: The secret key for JWT validation
            algorithm: The algorithm used for JWT encoding/decoding
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        # Routes that don't require authentication
        self.public_routes = {
            "/health",
            "/",
            "/openapi.json",
            "/docs",
            "/redoc",
            "/docs/oauth2-redirect",
        }

    async def dispatch(self, request: Request, call_next: Callable) -> object:
        """
        Process the request and validate JWT token if needed.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response or an error response if token is invalid
        """
        # Skip authentication for public routes
        if request.url.path in self.public_routes:
            return await call_next(request)

        # Skip authentication for OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning(f"Missing authorization header for {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning(f"Invalid authorization header format for {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = parts[1]

        try:
            # Decode and validate JWT token
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            # Add user info to request state for use in route handlers
            request.state.user = payload
            logger.debug(f"Token validated for user: {payload.get('sub')}")
        except JWTError as exc:
            logger.warning(f"JWT validation failed: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)


def create_access_token(data: dict, secret_key: str, expires_delta: Optional[timedelta] = None, algorithm: str = "HS256") -> str:
    """
    Create a JWT access token.

    Args:
        data: The payload data to encode
        secret_key: The secret key for encoding
        expires_delta: Optional expiration time delta
        algorithm: The algorithm to use for encoding

    Returns:
        The encoded JWT token as a string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
