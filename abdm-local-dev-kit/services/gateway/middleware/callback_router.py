"""
Callback Router Middleware

Handles async callback pattern for ABDM Gateway:
1. Routes requests from HIU/HIP/CM to appropriate services
2. Routes callbacks back to original requesters
3. Maintains callback URL mappings
4. Logs all transactions
"""

import httpx
import logging
from datetime import datetime
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class CallbackRouter:
    """
    Routes async callbacks in ABDM Gateway.

    ABDM uses async pattern:
    1. Client → Gateway: Request (sync 202 Accepted)
    2. Gateway → Service: Forward request
    3. Service → Gateway: Callback with result
    4. Gateway → Client: Forward callback to client's callback URL
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.service_urls = {
            "consent_manager": "http://consent-manager:8091",
            "hip": "http://hip:8092",
            "hiu": "http://hiu:8093"
        }

    async def route_to_service(
        self,
        service: str,
        endpoint: str,
        payload: Dict,
        request_id: str
    ) -> bool:
        """
        Route request to backend service (CM/HIP/HIU).

        Args:
            service: Service name (consent_manager, hip, hiu)
            endpoint: API endpoint path
            payload: Request payload
            request_id: Unique request ID for tracking

        Returns:
            True if successfully routed, False otherwise
        """
        if service not in self.service_urls:
            logger.error(f"Unknown service: {service}")
            return False

        service_url = self.service_urls[service]
        full_url = f"{service_url}{endpoint}"

        try:
            # Log transaction
            await self._log_transaction(
                transaction_id=request_id,
                direction="gateway_to_service",
                service=service,
                endpoint=endpoint,
                payload=payload
            )

            # Forward request to service
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    full_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                response.raise_for_status()
                logger.info(f"Routed request {request_id} to {service}{endpoint}: {response.status_code}")
                return True

        except httpx.HTTPStatusError as e:
            logger.error(f"Service {service} returned error {e.response.status_code}: {e.response.text}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Failed to route to {service}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error routing to {service}: {str(e)}")
            return False

    async def route_callback(
        self,
        callback_url: str,
        payload: Dict,
        request_id: str
    ) -> bool:
        """
        Route callback from service to original requester.

        Args:
            callback_url: URL to send callback to
            payload: Callback payload
            request_id: Request ID for tracking

        Returns:
            True if callback delivered, False otherwise
        """
        try:
            # Log callback
            await self._log_transaction(
                transaction_id=request_id,
                direction="gateway_to_client",
                service="callback",
                endpoint=callback_url,
                payload=payload
            )

            # Forward callback to requester
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    callback_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                response.raise_for_status()
                logger.info(f"Callback {request_id} delivered to {callback_url}: {response.status_code}")
                return True

        except httpx.HTTPStatusError as e:
            logger.error(f"Callback to {callback_url} failed {e.response.status_code}: {e.response.text}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Failed to deliver callback to {callback_url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error delivering callback: {str(e)}")
            return False

    async def register_callback_mapping(
        self,
        request_id: str,
        callback_url: str,
        metadata: Optional[Dict] = None
    ):
        """
        Register callback URL mapping for async response.

        Args:
            request_id: Unique request ID
            callback_url: URL to callback when response ready
            metadata: Additional metadata (e.g., requester ID, service type)
        """
        callback_mapping = {
            "request_id": request_id,
            "callback_url": callback_url,
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "delivered": False
        }

        await self.db.callback_mappings.insert_one(callback_mapping)
        logger.info(f"Registered callback mapping for request {request_id}")

    async def get_callback_url(self, request_id: str) -> Optional[str]:
        """
        Retrieve callback URL for a request ID.

        Args:
            request_id: Request ID

        Returns:
            Callback URL if found, None otherwise
        """
        mapping = await self.db.callback_mappings.find_one({"request_id": request_id})
        if mapping:
            return mapping.get("callback_url")
        return None

    async def mark_callback_delivered(self, request_id: str):
        """Mark callback as delivered."""
        await self.db.callback_mappings.update_one(
            {"request_id": request_id},
            {"$set": {"delivered": True, "delivered_at": datetime.now()}}
        )

    async def _log_transaction(
        self,
        transaction_id: str,
        direction: str,
        service: str,
        endpoint: str,
        payload: Dict
    ):
        """
        Log transaction for audit and debugging.

        Args:
            transaction_id: Transaction/request ID
            direction: gateway_to_service, service_to_gateway, gateway_to_client
            service: Service name
            endpoint: API endpoint
            payload: Request/response payload
        """
        transaction_log = {
            "transaction_id": transaction_id,
            "direction": direction,
            "service": service,
            "endpoint": endpoint,
            "payload": payload,
            "timestamp": datetime.now()
        }

        try:
            await self.db.transaction_logs.insert_one(transaction_log)
        except Exception as e:
            logger.error(f"Failed to log transaction: {str(e)}")


# Helper functions for common routing patterns

async def route_consent_request(
    router: CallbackRouter,
    consent_request: Dict,
    request_id: str,
    callback_url: str
) -> bool:
    """
    Route consent request from HIU to Consent Manager.

    Args:
        router: CallbackRouter instance
        consent_request: Consent request payload
        request_id: Request ID
        callback_url: HIU callback URL for response

    Returns:
        True if successfully routed
    """
    # Register callback mapping
    await router.register_callback_mapping(
        request_id=request_id,
        callback_url=callback_url,
        metadata={"type": "consent_request", "hiu_id": consent_request.get("consent", {}).get("hiu", {}).get("id")}
    )

    # Route to consent manager
    return await router.route_to_service(
        service="consent_manager",
        endpoint="/v0.5/consent-requests/on-init",
        payload=consent_request,
        request_id=request_id
    )


async def route_health_info_request(
    router: CallbackRouter,
    hi_request: Dict,
    request_id: str,
    callback_url: str
) -> bool:
    """
    Route health information request from CM to HIP.

    Args:
        router: CallbackRouter instance
        hi_request: Health info request payload
        request_id: Request ID
        callback_url: Callback URL for response

    Returns:
        True if successfully routed
    """
    # Register callback mapping
    await router.register_callback_mapping(
        request_id=request_id,
        callback_url=callback_url,
        metadata={"type": "health_info_request"}
    )

    # Route to HIP
    return await router.route_to_service(
        service="hip",
        endpoint="/v0.5/health-information/request",
        payload=hi_request,
        request_id=request_id
    )
