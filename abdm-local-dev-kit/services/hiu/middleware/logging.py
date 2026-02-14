import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP request and response details."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("hiu.requests")

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response details."""
        # Extract request information
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)

        # Record start time
        start_time = time.time()

        # Get request body if available
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
            except Exception as e:
                self.logger.warning(f"Failed to read request body: {e}")

        # Log incoming request
        self.logger.info(
            f"Request: {method} {path}",
            extra={
                "method": method,
                "path": path,
                "query_params": query_params,
            }
        )

        try:
            # Call the next middleware/endpoint
            response = await call_next(request)
        except Exception as e:
            # Log exception and re-raise
            process_time = time.time() - start_time
            self.logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                extra={
                    "method": method,
                    "path": path,
                    "duration": process_time,
                    "error": str(e),
                }
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        self.logger.info(
            f"Response: {method} {path} - {response.status_code}",
            extra={
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration": process_time,
            }
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)

        return response
