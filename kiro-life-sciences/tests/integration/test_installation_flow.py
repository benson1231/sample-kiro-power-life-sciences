"""Integration tests for the installation flow.

Tests end-to-end installation with a test manifest, dashboard generation
after install, and selective update.

**Validates: Requirements 2.1-2.5, 4.3, 6.1**
"""

from __future__ import annotations

import json

import pytest

from kiro_life_sciences.dashboard.renderer import DashboardRenderer
from kiro_life_sciences.installer.installer import (
    BundleInstaller,
    ComponentInstaller,
    InstallationResult,
)
from kiro_life_sciences.installer.updater import ManifestUpdater
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


class _RecordingInstaller:
    """Records which components were installed."""

    def __init__(self):
        self.installed: list[tuple[str, str]] = []

    def install_power(self, name: str, version: str) -> None:
        self.installed.append(("power", name))

    def install_mcp_server(self, name: str, version: str) -> None:
        self.installed.append(("mcp_server", name))

    def install_skill(self, name: str, filename: str) -> None:
        self.installed.append(("skill", name))

    def install_steering_file(self, name: str, filename: str) -> None:
        self.installed.append(("steering_file", name))

    def install_pipeline_registry(self, name: str) -> None:
        self.installed.append(("pipeline_registry", name))


def _test_manifest(version: str = "1.0.0") -> BundleManifest:
    """Build a small test manifest."""
    return BundleManifest(
        name="test-bundle",
        version=version,
        description="Test bundle for integration tests",
        components=BundleComponents(
            powers=[
                PowerReference(name="aws-healthomics", version="1.0.0", required=False, description="AHO"),
            ],
            mcpServers=[
                MCPServerReference(
                    name="life-sciences-genomics",
                    version="0.1.0",
                    pypiPackage="life-sciences-genomics",
                    description="Genomics server",
                    domain="Genomics and Sequencing",
                    databases=[
                        DatabaseReference(name="NCBI", description="NCBI databases", apiBaseUrl="https://eutils.ncbi.nlm.nih.gov/", authRequired=False, url="https://www.ncbi.nlm.nih.gov/"),
                    ],
                    credentials=[
                        CredentialRequirement(name="NCBI API Key", type="api_key", required=False, description="Optional", obtainUrl="https://ncbi.nlm.nih.gov/", envVar="NCBI_API_KEY"),
                    ],
                ),
                MCPServerReference(
                    name="life-sciences-proteomics",
                    version="0.1.0",
                    pypiPackage="life-sciences-proteomics",
                    description="Proteomics server",
                    domain="Proteomics",
                    databases=[
                        DatabaseReference(name="UniProt", description="UniProt", apiBaseUrl="https://rest.uniprot.org/", authRequired=False, url="https://www.uniprot.org/"),
                    ],
                ),
            ],
            skills=[
                SkillReference(name="Genomics Best Practices", filename="genomics.md", description="Genomics skill", domain="Genomics and Sequencing"),
            ],
            steeringFiles=[
                SteeringFileReference(name="Variant Calling", filename="variant-calling.md", description="Variant calling guide", domain="Genomics and Sequencing"),
            ],
            pipelineRegistries=[
                PipelineRegistryReference(name="nf-core", workflowLanguage="Nextflow", source="nf-core", description="nf-core pipelines"),
            ],
        ),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    )


class TestEndToEndInstallation:
    def test_full_installation(self):
        """Install all components from a test manifest."""
        manifest = _test_manifest()
        recorder = _RecordingInstaller()
        installer = BundleInstaller(recorder)
        result = installer.install(manifest)

        assert result.success
        assert result.installed_powers == 1
        assert result.installed_mcp_servers == 2
        assert result.installed_skills == 1
        assert result.installed_steering_files == 1
        assert result.installed_pipeline_registries == 1
        assert result.total_installed == 6

    def test_dashboard_after_install(self):
        """Generate dashboard after installation."""
        manifest = _test_manifest()
        installed_servers = {"life-sciences-genomics"}
        configured_creds: set[str] = set()

        renderer = DashboardRenderer(manifest, installed_servers, configured_creds)
        md = renderer.render_markdown()

        assert "Onboarding Dashboard" in md
        assert "NCBI" in md
        assert "UniProt" in md

    def test_selective_update(self):
        """Diff two manifests and verify only changed components are flagged."""
        v1 = _test_manifest("1.0.0")
        v2_components = v1.components.model_copy(
            update={
                "mcpServers": [
                    s.model_copy(update={"version": "0.2.0"}) if s.name == "life-sciences-genomics" else s
                    for s in v1.components.mcpServers
                ]
            }
        )
        v2 = v1.model_copy(update={"version": "1.1.0", "components": v2_components})

        updater = ManifestUpdater()
        diff = updater.diff(v1, v2)

        changed_names = {c.name for c in diff.changes}
        assert "life-sciences-genomics" in changed_names
        # proteomics unchanged
        assert "life-sciences-proteomics" not in changed_names
