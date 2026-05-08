"""Custom exception classes for Life Sciences MCP servers.

All API-related errors inherit from :class:`APIError`, which carries the
service name, HTTP status code (when applicable), and a human-readable
message.
"""

from __future__ import annotations


class APIError(Exception):
    """Base class for all Life Sciences API errors.

    Parameters
    ----------
    service:
        Name of the external service that produced the error (e.g. "NCBI").
    status_code:
        HTTP status code returned by the service, or ``None`` for
        non-HTTP errors such as timeouts.
    message:
        Human-readable description of the error.
    """

    def __init__(
        self,
        *,
        service: str,
        status_code: int | None = None,
        message: str,
    ) -> None:
        self.service = service
        self.status_code = status_code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        if self.status_code is not None:
            return f"[{self.service} {self.status_code}] {self.message}"
        return f"[{self.service}] {self.message}"


class RateLimitError(APIError):
    """Raised when rate-limit retries are exhausted (HTTP 429)."""

    def __init__(self, *, service: str, message: str | None = None) -> None:
        super().__init__(
            service=service,
            status_code=429,
            message=message or f"Rate limit exceeded for {service}. Try again later.",
        )


class AuthenticationError(APIError):
    """Raised on authentication / authorisation failures (HTTP 401/403).

    Parameters
    ----------
    obtain_url:
        URL where the user can obtain or refresh credentials.
    """

    def __init__(
        self,
        *,
        service: str,
        status_code: int = 401,
        obtain_url: str = "",
        message: str | None = None,
    ) -> None:
        self.obtain_url = obtain_url
        default_msg = f"Authentication failed for {service}."
        if obtain_url:
            default_msg += f" Please configure valid credentials: {obtain_url}"
        super().__init__(
            service=service,
            status_code=status_code,
            message=message or default_msg,
        )


class NotFoundError(APIError):
    """Raised when the requested resource is not found (HTTP 404)."""

    def __init__(
        self,
        *,
        service: str,
        query: str = "",
        message: str | None = None,
    ) -> None:
        self.query = query
        default_msg = f"No results found in {service}"
        if query:
            default_msg += f" for query '{query}'"
        default_msg += "."
        super().__init__(
            service=service,
            status_code=404,
            message=message or default_msg,
        )


class ServiceUnavailableError(APIError):
    """Raised on server errors (5xx) or when the service is unreachable."""

    def __init__(
        self,
        *,
        service: str,
        status_code: int | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(
            service=service,
            status_code=status_code,
            message=message or f"Service {service} is temporarily unavailable. Please try again.",
        )
