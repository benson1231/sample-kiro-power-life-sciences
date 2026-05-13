"""Credential management for the Kiro for Life Sciences bundle.

This package provides the :class:`CredentialManager` that stores, retrieves,
and deletes credentials in ``mcp.json`` using the ``${secret:key-name}``
syntax.  Credentials are **never** written to project files or version
control.
"""

from kiro_life_sciences.credentials.manager import (
    ConfiguredCredential,
    CredentialInstructions,
    CredentialManager,
)

__all__ = [
    "ConfiguredCredential",
    "CredentialInstructions",
    "CredentialManager",
]
