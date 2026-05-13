"""Pydantic models for the bundle manifest (``bundle-manifest.json``).

These models are the Python translation of the TypeScript interfaces defined in
the design document under *Components and Interfaces §1 — Bundle Manifest*.

All models use **Pydantic v2** conventions:
- ``model_config`` for configuration
- ``Field`` with ``pattern`` / ``min_length`` validators
- ``Literal`` types for constrained string unions
- ``model_json_schema()`` for JSON Schema generation
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from kiro_life_sciences.models.catalog import ResourceEntry


# ---------------------------------------------------------------------------
# Leaf / reference models (alphabetical)
# ---------------------------------------------------------------------------


class CredentialRequirement(BaseModel):
    """A credential that an MCP server needs to access an external service."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Credential display name, e.g. 'NCBI_API_KEY'.")
    type: Literal["api_key", "oauth", "username_password"] = Field(
        ..., description="Kind of credential."
    )
    required: bool = Field(..., description="Whether the credential is mandatory for the server to function.")
    description: str = Field(..., min_length=1, description="Human-readable explanation of the credential.")
    obtainUrl: str = Field(  # noqa: N815 — matches the TypeScript interface name
        ...,
        min_length=1,
        description="URL where the user can obtain or register for the credential.",
    )
    envVar: str = Field(  # noqa: N815
        ...,
        min_length=1,
        description="Environment variable name used to pass the credential to the MCP server.",
    )


class DatabaseReference(BaseModel):
    """Metadata for a single external database exposed by an MCP server."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Database display name, e.g. 'NCBI'.")
    description: str = Field(..., min_length=1, description="Short description of the database.")
    apiBaseUrl: str = Field(  # noqa: N815
        ...,
        min_length=1,
        description="Base URL of the database's API.",
    )
    authRequired: bool = Field(  # noqa: N815
        ..., description="Whether authentication is required to use this database."
    )
    credentialType: Literal["api_key", "oauth", "username_password"] | None = Field(  # noqa: N815
        default=None,
        description="Type of credential needed (only when authRequired is true).",
    )
    rateLimits: str | None = Field(  # noqa: N815
        default=None,
        description="Human-readable rate-limit description, e.g. '3 req/s without key'.",
    )
    license: str | None = Field(
        default=None,
        description="License or terms-of-use identifier for the database.",
    )
    exampleQueries: list[str] = Field(  # noqa: N815
        default_factory=list,
        description="Example queries a user can try.",
    )
    dataFormats: list[str] = Field(  # noqa: N815
        default_factory=list,
        description="Data formats returned by the database (e.g. 'FASTA', 'JSON').",
    )
    url: str = Field(
        ...,
        min_length=1,
        description="Documentation or home URL for the database.",
    )


class PipelineRegistryReference(BaseModel):
    """A reference to an external pipeline registry (nf-core, Broad, CWL, etc.)."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Pipeline registry name.")
    workflowLanguage: Literal["Nextflow", "WDL", "CWL", "mixed"] = Field(  # noqa: N815
        ..., description="Primary workflow language used by the registry."
    )
    source: str = Field(
        ...,
        min_length=1,
        description="Origin of the pipelines, e.g. 'nf-core', 'Broad Institute'.",
    )
    description: str = Field(..., min_length=1, description="Short description of the registry.")


class PowerReference(BaseModel):
    """A peer Kiro Power that the bundle depends on or recommends."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Power name, e.g. 'aws-healthomics'.")
    version: str = Field(..., min_length=1, description="Semver version of the Power.")
    required: bool = Field(..., description="Whether this Power is mandatory for the bundle.")
    description: str = Field(..., min_length=1, description="Short description of the Power.")


class SkillReference(BaseModel):
    """A domain-specific skill bundled with the Power."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Skill display name.")
    filename: str = Field(..., min_length=1, description="Filename inside the skills/ directory.")
    description: str = Field(..., min_length=1, description="Short description of the skill.")
    domain: str = Field(..., min_length=1, description="Life-sciences domain the skill covers.")


class SteeringFileReference(BaseModel):
    """A step-by-step workflow guide bundled with the Power."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Steering file display name.")
    filename: str = Field(..., min_length=1, description="Filename inside the steering/ directory.")
    description: str = Field(..., min_length=1, description="Short description of the steering file.")
    domain: str = Field(..., min_length=1, description="Life-sciences domain the guide covers.")
    relatedMCPServers: list[str] = Field(  # noqa: N815
        default_factory=list,
        description="Names of MCP servers referenced by this guide.",
    )


# ---------------------------------------------------------------------------
# Composite models
# ---------------------------------------------------------------------------


class MCPServerReference(BaseModel):
    """Metadata for a modular MCP server in the bundle."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="MCP server name, e.g. 'life-sciences-genomics'.")
    version: str = Field(..., min_length=1, description="Semver version of the server package.")
    pypiPackage: str = Field(  # noqa: N815
        ...,
        min_length=1,
        description="PyPI package name for installation via pip/uvx.",
    )
    description: str = Field(..., min_length=1, description="Short description of the server.")
    domain: str = Field(..., min_length=1, description="Life-sciences domain, e.g. 'Genomics and Sequencing'.")
    databases: list[DatabaseReference] = Field(
        default_factory=list,
        description="Databases exposed by this server.",
    )
    credentials: list[CredentialRequirement] = Field(
        default_factory=list,
        description="Credentials the server may need.",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Names of other MCP servers this server depends on.",
    )


class BundleComponents(BaseModel):
    """All component lists inside the bundle manifest."""

    model_config = ConfigDict(extra="forbid")

    powers: list[PowerReference] = Field(default_factory=list)
    mcpServers: list[MCPServerReference] = Field(default_factory=list)  # noqa: N815
    skills: list[SkillReference] = Field(default_factory=list)
    steeringFiles: list[SteeringFileReference] = Field(default_factory=list)  # noqa: N815
    pipelineRegistries: list[PipelineRegistryReference] = Field(default_factory=list)  # noqa: N815


class ResourceCatalogDefinition(BaseModel):
    """Top-level resource catalog section of the manifest.

    The ``entries`` list holds ``ResourceEntry`` objects from the catalog
    module.  The import is deferred to avoid a circular dependency between
    the manifest and catalog modules.
    """

    model_config = ConfigDict(extra="forbid")

    entries: list[ResourceEntry] = Field(
        default_factory=list,
        description="Flat list of resource entries indexed by the catalog engine.",
    )


# ---------------------------------------------------------------------------
# Top-level manifest
# ---------------------------------------------------------------------------

_SEMVER_PATTERN = r"^\d+\.\d+\.\d+$"


class BundleManifest(BaseModel):
    """Top-level schema for ``bundle-manifest.json``.

    Corresponds to the ``BundleManifest`` TypeScript interface in the design
    document.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Bundle name, e.g. 'kiro-life-sciences'.")
    version: str = Field(
        ...,
        pattern=_SEMVER_PATTERN,
        description="Bundle version following semantic versioning (MAJOR.MINOR.PATCH).",
    )
    description: str = Field(default="", description="Human-readable bundle description.")
    components: BundleComponents = Field(
        ..., description="All component references grouped by type."
    )
    resourceCatalog: ResourceCatalogDefinition = Field(  # noqa: N815
        ..., description="Resource catalog definition with entries."
    )
