"""Base MCP server class for all Life Sciences domain servers.

Provides an async HTTP client with:
* Exponential-backoff retry on 429 (rate-limit) responses
* Retry-After header support
* Single retry on 5xx server errors (2 s delay)
* Single retry on network timeouts (5 s delay)
* Standardised error mapping for 401/403/404/5xx/timeout/unreachable
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from mcp.server import Server

from life_sciences_common.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
)

logger = logging.getLogger(__name__)


class BaseLifeSciencesServer:
    """Base class for all life-sciences MCP servers."""

    def __init__(self, server_name: str) -> None:
        self.server = Server(server_name)
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=10),
        )

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute an HTTP request with retry logic.

        Retry behaviour
        ---------------
        * **429 (rate-limit)** – exponential backoff (1 s, 2 s, 4 s) up to
          *max_retries* attempts.  If the response includes a ``Retry-After``
          header the value is used instead.
        * **5xx (server error)** – single retry after a 2 s delay.
        * **Timeout** – single retry after a 5 s delay.
        * **Connection error** – no retry; raises immediately.
        """
        server_error_retried = False
        timeout_retried = False

        for attempt in range(max_retries + 1):
            try:
                response = await self.http_client.request(method, url, **kwargs)
            except httpx.TimeoutException:
                if not timeout_retried:
                    timeout_retried = True
                    logger.warning("Timeout contacting %s – retrying in 5 s", url)
                    await asyncio.sleep(5)
                    continue
                raise
            except httpx.ConnectError:
                raise

            # --- Rate-limit (429) ---
            if response.status_code == 429:
                if attempt < max_retries:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after is not None:
                        try:
                            wait_time = float(retry_after)
                        except (ValueError, TypeError):
                            wait_time = float(2**attempt)
                    else:
                        wait_time = float(2**attempt)  # 1, 2, 4 …
                    logger.info(
                        "Rate-limited on %s (attempt %d/%d) – waiting %.1f s",
                        url,
                        attempt + 1,
                        max_retries,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                # Retries exhausted
                raise RateLimitError(service=url)

            # --- Server error (5xx) ---
            if response.status_code >= 500:
                if not server_error_retried:
                    server_error_retried = True
                    logger.warning(
                        "Server error %d from %s – retrying in 2 s",
                        response.status_code,
                        url,
                    )
                    await asyncio.sleep(2)
                    continue
                return response

            return response

        # Should be unreachable, but guard anyway.
        raise RuntimeError("Unreachable: retry loop exited without returning")  # pragma: no cover

    async def _handle_api_error(
        self,
        response: httpx.Response,
        service_name: str,
        *,
        query: str = "",
        obtain_url: str = "",
    ) -> None:
        """Inspect *response* and raise the appropriate :class:`APIError`.

        Call this after :meth:`_request_with_retry` to convert non-2xx
        responses into typed exceptions.  2xx responses are silently
        ignored so callers can do::

            response = await self._request_with_retry("GET", url)
            await self._handle_api_error(response, "NCBI", query=term)
            # … use response …
        """
        status = response.status_code

        if 200 <= status < 300:
            return

        body = response.text

        if status in (401, 403):
            raise AuthenticationError(
                service=service_name,
                status_code=status,
                obtain_url=obtain_url,
            )

        if status == 404:
            raise NotFoundError(service=service_name, query=query)

        if status >= 500:
            raise ServiceUnavailableError(
                service=service_name,
                status_code=status,
                message=f"Service {service_name} is temporarily unavailable. Please try again.",
            )

        # Generic client error
        raise APIError(
            service=service_name,
            status_code=status,
            message=f"{service_name} returned {status}: {body}",
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def cleanup(self) -> None:
        """Close the underlying HTTP client."""
        await self.http_client.aclose()
