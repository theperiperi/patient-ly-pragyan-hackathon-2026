"""Request/Response Logging Middleware for HIP Service."""
import logging
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        # Extract request information
        method = request.method
        path = request.url.path
        query_string = request.url.query
        client_ip = request.client.host if request.client else "unknown"

        # Log request
        logger.info(
            f"[REQUEST] {method} {path}",
            extra={
                "method": method,
                "path": path,
                "query": query_string,
                "client_ip": client_ip,
            },
        )

        # Measure request processing time
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"[ERROR] {method} {path} - {str(exc)}",
                extra={
                    "method": method,
                    "path": path,
                    "process_time": process_time,
                    "error": str(exc),
                },
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"[RESPONSE] {method} {path} - {response.status_code}",
            extra={
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            },
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Service"] = "hip"

        return response
