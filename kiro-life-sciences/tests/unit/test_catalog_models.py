"""Unit tests for the resource catalog Pydantic models."""

import pytest
from pydantic import ValidationError

from kiro_life_sciences.models.catalog import (
    CatalogFilter,
    CatalogSearchResult,
    CrossReference,
    ResourceCategory,
    ResourceEntry,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_entry(**overrides) -> dict:
    """Return a minimal valid ResourceEntry dict, with optional overrides."""
    base = {
        "id": "ncbi-gene",
        "name": "NCBI Gene",
        "description": "NCBI Gene database",
        "category": "Genomics and Sequencing",
        "resourceType": "database",
        "url": "https://www.ncbi.nlm.nih.gov/gene/",
        "authRequired": False,
        "usageInstructions": "Search by gene symbol or ID.",
        "status": "needs_setup",
    }
    base.update(overrides)
    return base


def _database_entry(**overrides) -> dict:
    """Return a ResourceEntry dict with database-specific fields populated."""
    base = _minimal_entry(
        apiBaseUrl="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
        rateLimits="3 req/s without key, 10 req/s with key",
        license="Public Domain",
        exampleQueries=["BRCA1", "TP53"],
        dataFormats=["FASTA", "JSON", "XML"],
    )
    base.update(overrides)
    return base


def _pipeline_entry(**overrides) -> dict:
    """Return a ResourceEntry dict with pipeline-specific fields populated."""
    base = _minimal_entry(
        id="nfcore-rnaseq",
        name="nf-core/rnaseq",
        description="RNA sequencing analysis pipeline",
        category="Pipelines",
        resourceType="pipeline",
        url="https://nf-co.re/rnaseq",
        usageInstructions="Run with nextflow run nf-core/rnaseq.",
        workflowLanguage="Nextflow",
        sourceRepository="https://github.com/nf-core/rnaseq",
        pipelineVersion="3.14.0",
        requiredInputs=["samplesheet.csv", "genome reference"],
        expectedOutputs=["counts matrix", "QC report"],
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# ResourceCategory tests
# ---------------------------------------------------------------------------


class TestResourceCategory:
    """Tests for the ResourceCategory enum."""

    def test_has_25_categories(self):
        assert len(ResourceCategory) == 25

    def test_all_expected_categories_present(self):
        expected = [
            "Genomics and Sequencing",
            "Proteomics",
            "Pathways and Interactions",
            "Ontologies",
            "Clinical and Pharma",
            "Structural Biology",
            "Model Organisms",
            "Molecular Biology and Biochemistry",
            "Computational Chemistry and Drug Discovery",
            "Immunology",
            "Microbiology and Metagenomics",
            "Metabolomics",
            "Epigenomics",
            "Imaging and Microscopy",
            "Agricultural and Plant Biology",
            "Ecology and Environmental Biology",
            "Neuroscience",
            "Cell Biology",
            "Healthcare Standards",
            "Biobanking and Sample Management",
            "Pipelines",
            "Bioinformatics Analysis Tools",
            "Data Standards and Formats",
            "Cloud and HPC",
            "AI/ML for Life Sciences",
        ]
        actual_values = [c.value for c in ResourceCategory]
        assert sorted(actual_values) == sorted(expected)

    def test_category_is_str(self):
        """ResourceCategory members are strings (StrEnum)."""
        cat = ResourceCategory.GENOMICS_AND_SEQUENCING
        assert isinstance(cat, str)
        assert cat == "Genomics and Sequencing"

    def test_category_from_value(self):
        cat = ResourceCategory("Proteomics")
        assert cat is ResourceCategory.PROTEOMICS

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError):
            ResourceCategory("Not A Real Category")


# ---------------------------------------------------------------------------
# CrossReference tests
# ---------------------------------------------------------------------------


class TestCrossReference:
    """Tests for the CrossReference model."""

    def test_valid_cross_reference(self):
        cr = CrossReference(
            targetResourceId="uniprot",
            targetResourceName="UniProt",
            relationship="commonly used with",
        )
        assert cr.targetResourceId == "uniprot"
        assert cr.targetResourceName == "UniProt"
        assert cr.relationship == "commonly used with"

    def test_empty_target_id_rejected(self):
        with pytest.raises(ValidationError):
            CrossReference(
                targetResourceId="",
                targetResourceName="UniProt",
                relationship="commonly used with",
            )

    def test_empty_target_name_rejected(self):
        with pytest.raises(ValidationError):
            CrossReference(
                targetResourceId="uniprot",
                targetResourceName="",
                relationship="commonly used with",
            )

    def test_empty_relationship_rejected(self):
        with pytest.raises(ValidationError):
            CrossReference(
                targetResourceId="uniprot",
                targetResourceName="UniProt",
                relationship="",
            )

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            CrossReference(
                targetResourceId="uniprot",
                targetResourceName="UniProt",
                relationship="commonly used with",
                extraField="nope",
            )


# ---------------------------------------------------------------------------
# ResourceEntry tests
# ---------------------------------------------------------------------------


class TestResourceEntry:
    """Tests for the ResourceEntry model."""

    def test_minimal_entry_valid(self):
        entry = ResourceEntry(**_minimal_entry())
        assert entry.id == "ncbi-gene"
        assert entry.name == "NCBI Gene"
        assert entry.category == ResourceCategory.GENOMICS_AND_SEQUENCING
        assert entry.resourceType == "database"
        assert entry.authRequired is False
        assert entry.status == "needs_setup"

    def test_defaults_for_optional_fields(self):
        entry = ResourceEntry(**_minimal_entry())
        assert entry.credentialType is None
        assert entry.dataFormats == []
        assert entry.mcpServer is None
        assert entry.mcpServerInstalled is False
        assert entry.credentialsConfigured is False
        assert entry.crossReferences == []
        # Database-specific defaults
        assert entry.apiBaseUrl is None
        assert entry.rateLimits is None
        assert entry.license is None
        assert entry.exampleQueries is None
        # Pipeline-specific defaults
        assert entry.workflowLanguage is None
        assert entry.sourceRepository is None
        assert entry.pipelineVersion is None
        assert entry.requiredInputs is None
        assert entry.expectedOutputs is None

    def test_database_entry_with_all_fields(self):
        entry = ResourceEntry(**_database_entry())
        assert entry.apiBaseUrl is not None
        assert entry.rateLimits == "3 req/s without key, 10 req/s with key"
        assert entry.license == "Public Domain"
        assert entry.exampleQueries == ["BRCA1", "TP53"]
        assert entry.dataFormats == ["FASTA", "JSON", "XML"]

    def test_pipeline_entry_with_all_fields(self):
        entry = ResourceEntry(**_pipeline_entry())
        assert entry.workflowLanguage == "Nextflow"
        assert entry.sourceRepository == "https://github.com/nf-core/rnaseq"
        assert entry.pipelineVersion == "3.14.0"
        assert entry.requiredInputs == ["samplesheet.csv", "genome reference"]
        assert entry.expectedOutputs == ["counts matrix", "QC report"]

    def test_entry_with_cross_references(self):
        entry = ResourceEntry(
            **_minimal_entry(
                crossReferences=[
                    {
                        "targetResourceId": "uniprot",
                        "targetResourceName": "UniProt",
                        "relationship": "commonly used with",
                    },
                    {
                        "targetResourceId": "kegg",
                        "targetResourceName": "KEGG",
                        "relationship": "provides data for",
                    },
                ],
            )
        )
        assert len(entry.crossReferences) == 2
        assert entry.crossReferences[0].targetResourceId == "uniprot"
        assert entry.crossReferences[1].relationship == "provides data for"

    def test_entry_with_mcp_server(self):
        entry = ResourceEntry(
            **_minimal_entry(
                mcpServer="life-sciences-genomics",
                mcpServerInstalled=True,
                credentialsConfigured=True,
                status="ready",
            )
        )
        assert entry.mcpServer == "life-sciences-genomics"
        assert entry.mcpServerInstalled is True
        assert entry.credentialsConfigured is True
        assert entry.status == "ready"

    def test_round_trip_json(self):
        original = ResourceEntry(**_database_entry())
        json_str = original.model_dump_json()
        restored = ResourceEntry.model_validate_json(json_str)
        assert restored == original

    def test_round_trip_dict(self):
        original = ResourceEntry(**_pipeline_entry())
        d = original.model_dump()
        restored = ResourceEntry.model_validate(d)
        assert restored == original

    # -- Validation: required fields --

    def test_id_required(self):
        data = _minimal_entry()
        del data["id"]
        with pytest.raises(ValidationError):
            ResourceEntry(**data)

    def test_id_cannot_be_empty(self):
        with pytest.raises(ValidationError):
            ResourceEntry(**_minimal_entry(id=""))

    def test_name_required(self):
        data = _minimal_entry()
        del data["name"]
        with pytest.raises(ValidationError):
            ResourceEntry(**data)

    def test_description_required(self):
        data = _minimal_entry()
        del data["description"]
        with pytest.raises(ValidationError):
            ResourceEntry(**data)

    def test_category_required(self):
        data = _minimal_entry()
        del data["category"]
        with pytest.raises(ValidationError):
            ResourceEntry(**data)

    def test_status_required(self):
        data = _minimal_entry()
        del data["status"]
        with pytest.raises(ValidationError):
            ResourceEntry(**data)

    def test_usage_instructions_required(self):
        data = _minimal_entry()
        del data["usageInstructions"]
        with pytest.raises(ValidationError):
            ResourceEntry(**data)

    # -- Validation: constrained values --

    def test_invalid_resource_type_rejected(self):
        with pytest.raises(ValidationError):
            ResourceEntry(**_minimal_entry(resourceType="notebook"))

    @pytest.mark.parametrize(
        "resource_type",
        ["database", "pipeline", "tool", "skill", "steering_file"],
    )
    def test_valid_resource_types(self, resource_type):
        entry = ResourceEntry(**_minimal_entry(resourceType=resource_type))
        assert entry.resourceType == resource_type

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            ResourceEntry(**_minimal_entry(status="broken"))

    @pytest.mark.parametrize("status", ["ready", "needs_setup", "needs_credentials"])
    def test_valid_statuses(self, status):
        entry = ResourceEntry(**_minimal_entry(status=status))
        assert entry.status == status

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            ResourceEntry(**_minimal_entry(category="Alchemy"))

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            ResourceEntry(**_minimal_entry(extraField="nope"))


# ---------------------------------------------------------------------------
# CatalogFilter tests
# ---------------------------------------------------------------------------


class TestCatalogFilter:
    """Tests for the CatalogFilter model."""

    def test_empty_filter(self):
        f = CatalogFilter()
        assert f.category is None
        assert f.resourceType is None
        assert f.authRequirement is None

    def test_filter_with_category(self):
        f = CatalogFilter(category="Proteomics")
        assert f.category == ResourceCategory.PROTEOMICS

    def test_filter_with_resource_type(self):
        f = CatalogFilter(resourceType="pipeline")
        assert f.resourceType == "pipeline"

    def test_filter_with_auth_requirement(self):
        f = CatalogFilter(authRequirement="authenticated")
        assert f.authRequirement == "authenticated"

    def test_filter_open_access(self):
        f = CatalogFilter(authRequirement="open_access")
        assert f.authRequirement == "open_access"

    def test_filter_all_fields(self):
        f = CatalogFilter(
            category="Genomics and Sequencing",
            resourceType="database",
            authRequirement="open_access",
        )
        assert f.category == ResourceCategory.GENOMICS_AND_SEQUENCING
        assert f.resourceType == "database"
        assert f.authRequirement == "open_access"

    def test_invalid_resource_type_rejected(self):
        with pytest.raises(ValidationError):
            CatalogFilter(resourceType="widget")

    def test_invalid_auth_requirement_rejected(self):
        with pytest.raises(ValidationError):
            CatalogFilter(authRequirement="maybe")

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            CatalogFilter(category="Alchemy")

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            CatalogFilter(extraField="nope")


# ---------------------------------------------------------------------------
# CatalogSearchResult tests
# ---------------------------------------------------------------------------


class TestCatalogSearchResult:
    """Tests for the CatalogSearchResult model."""

    def test_empty_result(self):
        result = CatalogSearchResult(
            entries=[],
            totalCount=0,
            query="BRCA1",
            filters=CatalogFilter(),
        )
        assert result.entries == []
        assert result.totalCount == 0
        assert result.query == "BRCA1"

    def test_result_with_entries(self):
        entry = ResourceEntry(**_minimal_entry())
        result = CatalogSearchResult(
            entries=[entry],
            totalCount=1,
            query="NCBI",
            filters=CatalogFilter(category="Genomics and Sequencing"),
        )
        assert len(result.entries) == 1
        assert result.totalCount == 1
        assert result.filters.category == ResourceCategory.GENOMICS_AND_SEQUENCING

    def test_negative_total_count_rejected(self):
        with pytest.raises(ValidationError):
            CatalogSearchResult(
                entries=[],
                totalCount=-1,
                query="test",
                filters=CatalogFilter(),
            )

    def test_round_trip_json(self):
        entry = ResourceEntry(**_minimal_entry())
        original = CatalogSearchResult(
            entries=[entry],
            totalCount=1,
            query="gene",
            filters=CatalogFilter(resourceType="database"),
        )
        json_str = original.model_dump_json()
        restored = CatalogSearchResult.model_validate_json(json_str)
        assert restored == original

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            CatalogSearchResult(
                entries=[],
                totalCount=0,
                query="test",
                filters=CatalogFilter(),
                extraField="nope",
            )


# ---------------------------------------------------------------------------
# Integration: ResourceEntry inside ResourceCatalogDefinition
# ---------------------------------------------------------------------------


class TestResourceCatalogDefinitionIntegration:
    """Verify ResourceEntry works inside the manifest's ResourceCatalogDefinition."""

    def test_catalog_definition_accepts_resource_entries(self):
        from kiro_life_sciences.models.manifest import ResourceCatalogDefinition

        entry = ResourceEntry(**_database_entry())
        catalog = ResourceCatalogDefinition(entries=[entry])
        assert len(catalog.entries) == 1
        assert catalog.entries[0].name == "NCBI Gene"

    def test_catalog_definition_empty(self):
        from kiro_life_sciences.models.manifest import ResourceCatalogDefinition

        catalog = ResourceCatalogDefinition(entries=[])
        assert catalog.entries == []

    def test_manifest_with_resource_entries(self):
        from kiro_life_sciences.models.manifest import (
            BundleComponents,
            BundleManifest,
            ResourceCatalogDefinition,
        )

        entry = ResourceEntry(**_minimal_entry())
        manifest = BundleManifest(
            name="kiro-life-sciences",
            version="1.0.0",
            components=BundleComponents(
                powers=[],
                mcpServers=[],
                skills=[],
                steeringFiles=[],
                pipelineRegistries=[],
            ),
            resourceCatalog=ResourceCatalogDefinition(entries=[entry]),
        )
        assert len(manifest.resourceCatalog.entries) == 1
        assert manifest.resourceCatalog.entries[0].id == "ncbi-gene"
