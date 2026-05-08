"""Shared base package for all Kiro Life Sciences MCP servers."""

from life_sciences_common.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
)
from life_sciences_common.server import BaseLifeSciencesServer

__all__ = [
    "BaseLifeSciencesServer",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
]
