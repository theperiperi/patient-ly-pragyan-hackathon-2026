import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> StreamingResponse:
        """Log incoming requests and outgoing responses."""

        request_id = request.headers.get("x-request-id", "N/A")
        start_time = time.time()

        # Log request details
        logger.info(
            f"Request ID: {request_id} | Method: {request.method} | "
            f"Path: {request.url.path} | Client: {request.client.host if request.client else 'Unknown'}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response details
            logger.info(
                f"Request ID: {request_id} | Status: {response.status_code} | "
                f"Duration: {process_time:.3f}s"
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Request ID: {request_id} | Error: {str(exc)} | "
                f"Duration: {process_time:.3f}s",
                exc_info=True
            )
            raise
