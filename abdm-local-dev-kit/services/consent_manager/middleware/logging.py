"""
Logging middleware for request/response tracking.
Logs all HTTP requests and responses with timing information.
"""

import logging
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests and responses.
    Includes request path, method, status code, and response time.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and response, logging relevant information.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response from the route handler
        """
        # Extract request information
        method = request.method
        url = request.url.path
        query_params = dict(request.query_params) if request.query_params else {}

        # Log incoming request
        logger.info(
            f"Incoming Request",
            extra={
                "method": method,
                "path": url,
                "query_params": query_params,
            },
        )

        # Record start time
        start_time = time.time()

        try:
            # Call the next middleware or route handler
            response = await call_next(request)
        except Exception as exc:
            # Log the exception
            process_time = time.time() - start_time
            logger.error(
                f"Request failed with exception",
                extra={
                    "method": method,
                    "path": url,
                    "process_time": f"{process_time:.3f}s",
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

        # Calculate process time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response",
            extra={
                "method": method,
                "path": url,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            },
        )

        # Add custom headers to response
        response.headers["X-Process-Time"] = str(process_time)

        return response
