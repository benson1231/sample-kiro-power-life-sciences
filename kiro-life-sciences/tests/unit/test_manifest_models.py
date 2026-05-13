"""Unit tests for the bundle manifest Pydantic models."""

import json

import pytest
from pydantic import ValidationError

from kiro_life_sciences.models.manifest import (
    BundleComponents,
    BundleManifest,
    CredentialRequirement,
    DatabaseReference,
    MCPServerReference,
    PipelineRegistryReference,
    PowerReference,
    ResourceCatalogDefinition,
    SkillReference,
    SteeringFileReference,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_manifest(**overrides) -> dict:
    """Return a minimal valid manifest dict, with optional overrides."""
    base = {
        "name": "kiro-life-sciences",
        "version": "1.0.0",
        "description": "Test bundle",
        "components": {
            "powers": [],
            "mcpServers": [],
            "skills": [],
            "steeringFiles": [],
            "pipelineRegistries": [],
        },
        "resourceCatalog": {"entries": []},
    }
    base.update(overrides)
    return base


def _full_manifest() -> BundleManifest:
    """Build a manifest with at least one of every component type."""
    return BundleManifest(
        name="kiro-life-sciences",
        version="2.1.0",
        description="Full test bundle",
        components=BundleComponents(
            powers=[
                PowerReference(
                    name="aws-healthomics",
                    version="1.0.0",
                    required=True,
                    description="AWS HealthOmics Power",
                ),
            ],
            mcpServers=[
                MCPServerReference(
                    name="life-sciences-genomics",
                    version="1.0.0",
                    pypiPackage="life-sciences-genomics",
                    description="Genomics MCP server",
                    domain="Genomics and Sequencing",
                    databases=[
                        DatabaseReference(
                            name="NCBI",
                            description="NCBI databases",
                            apiBaseUrl="https://eutils.ncbi.nlm.nih.gov/",
                            authRequired=False,
                            rateLimits="3 req/s",
                            exampleQueries=["BRCA1"],
                            dataFormats=["FASTA", "JSON"],
                            url="https://www.ncbi.nlm.nih.gov/",
                        ),
                    ],
                    credentials=[
                        CredentialRequirement(
                            name="NCBI API Key",
                            type="api_key",
                            required=False,
                            description="Increases rate limit",
                            obtainUrl="https://www.ncbi.nlm.nih.gov/account/settings/",
                            envVar="NCBI_API_KEY",
                        ),
                    ],
                    dependencies=[],
                ),
            ],
            skills=[
                SkillReference(
                    name="File Formats",
                    filename="file-formats.md",
                    description="Guide to file formats",
                    domain="General",
                ),
            ],
            steeringFiles=[
                SteeringFileReference(
                    name="Variant Calling",
                    filename="variant-calling.md",
                    description="Variant calling guide",
                    domain="Genomics",
                    relatedMCPServers=["life-sciences-genomics"],
                ),
            ],
            pipelineRegistries=[
                PipelineRegistryReference(
                    name="nf-core",
                    workflowLanguage="Nextflow",
                    source="nf-core",
                    description="Community Nextflow pipelines",
                ),
            ],
        ),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    )


# ---------------------------------------------------------------------------
# BundleManifest tests
# ---------------------------------------------------------------------------


class TestBundleManifest:
    """Tests for the top-level BundleManifest model."""

    def test_minimal_manifest_valid(self):
        m = BundleManifest(**_minimal_manifest())
        assert m.name == "kiro-life-sciences"
        assert m.version == "1.0.0"

    def test_full_manifest_valid(self):
        m = _full_manifest()
        assert len(m.components.powers) == 1
        assert len(m.components.mcpServers) == 1
        assert len(m.components.skills) == 1
        assert len(m.components.steeringFiles) == 1
        assert len(m.components.pipelineRegistries) == 1

    def test_round_trip_json(self):
        original = _full_manifest()
        json_str = original.model_dump_json()
        restored = BundleManifest.model_validate_json(json_str)
        assert restored == original

    def test_round_trip_dict(self):
        original = _full_manifest()
        d = original.model_dump()
        restored = BundleManifest.model_validate(d)
        assert restored == original

    def test_json_schema_generation(self):
        schema = BundleManifest.model_json_schema()
        assert "properties" in schema
        props = schema["properties"]
        assert "name" in props
        assert "version" in props
        assert "components" in props
        assert "resourceCatalog" in props

    def test_version_must_be_semver(self):
        with pytest.raises(ValidationError, match="string_pattern_mismatch"):
            BundleManifest(**_minimal_manifest(version="not-semver"))

    def test_version_rejects_partial_semver(self):
        with pytest.raises(ValidationError):
            BundleManifest(**_minimal_manifest(version="1.0"))

    def test_version_rejects_leading_v(self):
        with pytest.raises(ValidationError):
            BundleManifest(**_minimal_manifest(version="v1.0.0"))

    def test_name_required(self):
        data = _minimal_manifest()
        del data["name"]
        with pytest.raises(ValidationError):
            BundleManifest(**data)

    def test_name_cannot_be_empty(self):
        with pytest.raises(ValidationError):
            BundleManifest(**_minimal_manifest(name=""))

    def test_components_required(self):
        data = _minimal_manifest()
        del data["components"]
        with pytest.raises(ValidationError):
            BundleManifest(**data)

    def test_resource_catalog_required(self):
        data = _minimal_manifest()
        del data["resourceCatalog"]
        with pytest.raises(ValidationError):
            BundleManifest(**data)

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            BundleManifest(**_minimal_manifest(extraField="nope"))

    def test_description_defaults_to_empty(self):
        data = _minimal_manifest()
        del data["description"]
        m = BundleManifest(**data)
        assert m.description == ""


# ---------------------------------------------------------------------------
# CredentialRequirement tests
# ---------------------------------------------------------------------------


class TestCredentialRequirement:
    """Tests for the CredentialRequirement model."""

    def test_valid_api_key(self):
        c = CredentialRequirement(
            name="KEY", type="api_key", required=True,
            description="An API key", obtainUrl="https://example.com", envVar="MY_KEY",
        )
        assert c.type == "api_key"

    def test_valid_oauth(self):
        c = CredentialRequirement(
            name="TOKEN", type="oauth", required=False,
            description="OAuth token", obtainUrl="https://example.com", envVar="TOKEN",
        )
        assert c.type == "oauth"

    def test_valid_username_password(self):
        c = CredentialRequirement(
            name="CREDS", type="username_password", required=True,
            description="User/pass", obtainUrl="https://example.com", envVar="CREDS",
        )
        assert c.type == "username_password"

    def test_invalid_type_rejected(self):
        with pytest.raises(ValidationError):
            CredentialRequirement(
                name="X", type="bearer_token", required=True,
                description="bad", obtainUrl="https://example.com", envVar="X",
            )


# ---------------------------------------------------------------------------
# DatabaseReference tests
# ---------------------------------------------------------------------------


class TestDatabaseReference:
    """Tests for the DatabaseReference model."""

    def test_minimal_database(self):
        db = DatabaseReference(
            name="TestDB", description="A test database",
            apiBaseUrl="https://api.test.com", authRequired=False,
            url="https://test.com",
        )
        assert db.credentialType is None
        assert db.rateLimits is None
        assert db.license is None
        assert db.exampleQueries == []
        assert db.dataFormats == []

    def test_full_database(self):
        db = DatabaseReference(
            name="NCBI", description="NCBI databases",
            apiBaseUrl="https://eutils.ncbi.nlm.nih.gov/",
            authRequired=True, credentialType="api_key",
            rateLimits="10 req/s", license="Public Domain",
            exampleQueries=["BRCA1", "TP53"],
            dataFormats=["FASTA", "JSON"],
            url="https://www.ncbi.nlm.nih.gov/",
        )
        assert db.credentialType == "api_key"
        assert len(db.exampleQueries) == 2

    def test_invalid_credential_type(self):
        with pytest.raises(ValidationError):
            DatabaseReference(
                name="X", description="X",
                apiBaseUrl="https://x.com", authRequired=True,
                credentialType="magic_token",
                url="https://x.com",
            )


# ---------------------------------------------------------------------------
# PipelineRegistryReference tests
# ---------------------------------------------------------------------------


class TestPipelineRegistryReference:
    """Tests for the PipelineRegistryReference model."""

    @pytest.mark.parametrize("lang", ["Nextflow", "WDL", "CWL", "mixed"])
    def test_valid_workflow_languages(self, lang):
        p = PipelineRegistryReference(
            name="test", workflowLanguage=lang, source="test", description="test",
        )
        assert p.workflowLanguage == lang

    def test_invalid_workflow_language(self):
        with pytest.raises(ValidationError):
            PipelineRegistryReference(
                name="test", workflowLanguage="Snakemake",
                source="test", description="test",
            )


# ---------------------------------------------------------------------------
# MCPServerReference tests
# ---------------------------------------------------------------------------


class TestMCPServerReference:
    """Tests for the MCPServerReference model."""

    def test_minimal_server(self):
        s = MCPServerReference(
            name="life-sciences-genomics", version="1.0.0",
            pypiPackage="life-sciences-genomics",
            description="Genomics", domain="Genomics and Sequencing",
        )
        assert s.databases == []
        assert s.credentials == []
        assert s.dependencies == []

    def test_server_with_databases_and_credentials(self):
        s = MCPServerReference(
            name="life-sciences-genomics", version="1.0.0",
            pypiPackage="life-sciences-genomics",
            description="Genomics", domain="Genomics and Sequencing",
            databases=[
                DatabaseReference(
                    name="NCBI", description="NCBI",
                    apiBaseUrl="https://api.ncbi.nlm.nih.gov/",
                    authRequired=False, url="https://ncbi.nlm.nih.gov/",
                ),
            ],
            credentials=[
                CredentialRequirement(
                    name="KEY", type="api_key", required=False,
                    description="key", obtainUrl="https://ncbi.nlm.nih.gov/",
                    envVar="NCBI_API_KEY",
                ),
            ],
            dependencies=["life-sciences-common"],
        )
        assert len(s.databases) == 1
        assert len(s.credentials) == 1
        assert s.dependencies == ["life-sciences-common"]


# ---------------------------------------------------------------------------
# SteeringFileReference tests
# ---------------------------------------------------------------------------


class TestSteeringFileReference:
    """Tests for the SteeringFileReference model."""

    def test_with_related_servers(self):
        sf = SteeringFileReference(
            name="Guide", filename="guide.md",
            description="A guide", domain="Genomics",
            relatedMCPServers=["life-sciences-genomics", "life-sciences-clinical"],
        )
        assert len(sf.relatedMCPServers) == 2

    def test_defaults_to_empty_related_servers(self):
        sf = SteeringFileReference(
            name="Guide", filename="guide.md",
            description="A guide", domain="Genomics",
        )
        assert sf.relatedMCPServers == []
