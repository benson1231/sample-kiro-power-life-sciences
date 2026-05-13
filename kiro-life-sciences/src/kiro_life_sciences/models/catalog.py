"""Pydantic models for the resource catalog.

These models are the Python translation of the TypeScript interfaces defined in
the design document under *Components and Interfaces §2 — Resource Catalog Engine*.

All models use **Pydantic v2** conventions:
- ``model_config = ConfigDict(extra="forbid")``
- ``Field`` with validators
- ``StrEnum`` for the category enumeration
- ``Literal`` types for constrained string unions
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ResourceCategory(StrEnum):
    """All 25 resource categories defined in the design document."""

    GENOMICS_AND_SEQUENCING = "Genomics and Sequencing"
    PROTEOMICS = "Proteomics"
    PATHWAYS_AND_INTERACTIONS = "Pathways and Interactions"
    ONTOLOGIES = "Ontologies"
    CLINICAL_AND_PHARMA = "Clinical and Pharma"
    STRUCTURAL_BIOLOGY = "Structural Biology"
    MODEL_ORGANISMS = "Model Organisms"
    MOLECULAR_BIOLOGY_AND_BIOCHEMISTRY = "Molecular Biology and Biochemistry"
    COMPUTATIONAL_CHEMISTRY_AND_DRUG_DISCOVERY = "Computational Chemistry and Drug Discovery"
    IMMUNOLOGY = "Immunology"
    MICROBIOLOGY_AND_METAGENOMICS = "Microbiology and Metagenomics"
    METABOLOMICS = "Metabolomics"
    EPIGENOMICS = "Epigenomics"
    IMAGING_AND_MICROSCOPY = "Imaging and Microscopy"
    AGRICULTURAL_AND_PLANT_BIOLOGY = "Agricultural and Plant Biology"
    ECOLOGY_AND_ENVIRONMENTAL_BIOLOGY = "Ecology and Environmental Biology"
    NEUROSCIENCE = "Neuroscience"
    CELL_BIOLOGY = "Cell Biology"
    HEALTHCARE_STANDARDS = "Healthcare Standards"
    BIOBANKING_AND_SAMPLE_MANAGEMENT = "Biobanking and Sample Management"
    PIPELINES = "Pipelines"
    BIOINFORMATICS_ANALYSIS_TOOLS = "Bioinformatics Analysis Tools"
    DATA_STANDARDS_AND_FORMATS = "Data Standards and Formats"
    CLOUD_AND_HPC = "Cloud and HPC"
    AI_ML_FOR_LIFE_SCIENCES = "AI/ML for Life Sciences"


# ---------------------------------------------------------------------------
# Leaf models
# ---------------------------------------------------------------------------


class CrossReference(BaseModel):
    """A cross-reference linking one resource to another."""

    model_config = ConfigDict(extra="forbid")

    targetResourceId: str = Field(  # noqa: N815
        ...,
        min_length=1,
        description="Unique identifier of the target resource.",
    )
    targetResourceName: str = Field(  # noqa: N815
        ...,
        min_length=1,
        description="Display name of the target resource.",
    )
    relationship: str = Field(
        ...,
        min_length=1,
        description="Relationship description, e.g. 'commonly used with', 'provides data for'.",
    )


# ---------------------------------------------------------------------------
# Core resource entry
# ---------------------------------------------------------------------------


class ResourceEntry(BaseModel):
    """A single record in the resource catalog.

    Contains metadata about a database, pipeline, tool, skill, or steering
    file.  Database-specific and pipeline-specific optional fields are included
    so that a single flat model can represent all resource types.
    """

    model_config = ConfigDict(extra="forbid")

    # -- Core fields (required for every resource) --
    id: str = Field(..., min_length=1, description="Unique identifier for the resource.")
    name: str = Field(..., min_length=1, description="Display name of the resource.")
    description: str = Field(..., min_length=1, description="Short description of the resource.")
    category: ResourceCategory = Field(..., description="Category the resource belongs to.")
    resourceType: Literal["database", "pipeline", "tool", "skill", "steering_file"] = Field(  # noqa: N815
        ..., description="Kind of resource."
    )
    url: str = Field(..., min_length=1, description="Documentation or home URL for the resource.")
    authRequired: bool = Field(  # noqa: N815
        ..., description="Whether authentication is required to use this resource."
    )
    credentialType: str | None = Field(  # noqa: N815
        default=None,
        description="Type of credential needed (only when authRequired is true).",
    )
    dataFormats: list[str] = Field(  # noqa: N815
        default_factory=list,
        description="Data formats supported or returned by the resource.",
    )
    usageInstructions: str = Field(  # noqa: N815
        ...,
        min_length=1,
        description="Human-readable usage instructions for the resource.",
    )
    mcpServer: str | None = Field(  # noqa: N815
        default=None,
        description="Name of the MCP server that provides this resource.",
    )
    mcpServerInstalled: bool = Field(  # noqa: N815
        default=False,
        description="Whether the MCP server is currently installed (runtime status).",
    )
    credentialsConfigured: bool = Field(  # noqa: N815
        default=False,
        description="Whether required credentials are configured (runtime status).",
    )
    status: Literal["ready", "needs_setup", "needs_credentials"] = Field(
        ...,
        description=(
            "Computed status: 'ready' if server installed and credentials configured, "
            "'needs_credentials' if server installed but credentials missing, "
            "'needs_setup' if server not installed."
        ),
    )
    crossReferences: list[CrossReference] = Field(  # noqa: N815
        default_factory=list,
        description="Cross-references to related resources.",
    )

    # -- Database-specific optional fields --
    apiBaseUrl: str | None = Field(  # noqa: N815
        default=None,
        description="Base URL of the database's API.",
    )
    rateLimits: str | None = Field(  # noqa: N815
        default=None,
        description="Human-readable rate-limit description.",
    )
    license: str | None = Field(
        default=None,
        description="License or terms-of-use identifier.",
    )
    exampleQueries: list[str] | None = Field(  # noqa: N815
        default=None,
        description="Example queries a user can try.",
    )

    # -- Pipeline-specific optional fields --
    workflowLanguage: str | None = Field(  # noqa: N815
        default=None,
        description="Workflow language (e.g. 'Nextflow', 'WDL', 'CWL').",
    )
    sourceRepository: str | None = Field(  # noqa: N815
        default=None,
        description="Source repository URL for the pipeline.",
    )
    pipelineVersion: str | None = Field(  # noqa: N815
        default=None,
        description="Version of the pipeline.",
    )
    requiredInputs: list[str] | None = Field(  # noqa: N815
        default=None,
        description="Required input descriptions for the pipeline.",
    )
    expectedOutputs: list[str] | None = Field(  # noqa: N815
        default=None,
        description="Expected output descriptions for the pipeline.",
    )


# ---------------------------------------------------------------------------
# Search / filter models
# ---------------------------------------------------------------------------


class CatalogFilter(BaseModel):
    """Filter criteria for catalog search and browse operations."""

    model_config = ConfigDict(extra="forbid")

    category: ResourceCategory | None = Field(
        default=None,
        description="Filter by resource category.",
    )
    resourceType: Literal["database", "pipeline", "tool", "skill", "steering_file"] | None = Field(  # noqa: N815
        default=None,
        description="Filter by resource type.",
    )
    authRequirement: Literal["authenticated", "open_access"] | None = Field(  # noqa: N815
        default=None,
        description="Filter by authentication requirement.",
    )


class CatalogSearchResult(BaseModel):
    """Result set returned by a catalog search operation."""

    model_config = ConfigDict(extra="forbid")

    entries: list[ResourceEntry] = Field(
        default_factory=list,
        description="Matching resource entries.",
    )
    totalCount: int = Field(  # noqa: N815
        ...,
        ge=0,
        description="Total number of matching entries.",
    )
    query: str = Field(
        ...,
        description="The search keyword that was used.",
    )
    filters: CatalogFilter = Field(
        ...,
        description="The filters that were applied.",
    )
