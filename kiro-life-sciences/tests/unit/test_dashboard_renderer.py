"""Unit tests for the onboarding dashboard renderer."""

import pytest

from kiro_life_sciences.dashboard.renderer import (
    DashboardCategory,
    DashboardData,
    DashboardRenderer,
    DashboardResource,
    DashboardSummary,
    compute_resource_status,
)
from kiro_life_sciences.models.catalog import ResourceCategory
from kiro_life_sciences.models.manifest import (
    BundleComponents,
    BundleManifest,
    CredentialRequirement,
    DatabaseReference,
    MCPServerReference,
    PipelineRegistryReference,
    ResourceCatalogDefinition,
    SkillReference,
    SteeringFileReference,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _db(**overrides) -> DatabaseReference:
    """Build a minimal DatabaseReference with optional overrides."""
    base = {
        "name": "TestDB",
        "description": "A test database.",
        "apiBaseUrl": "https://api.test.com/",
        "authRequired": False,
        "url": "https://test.com/",
    }
    base.update(overrides)
    return DatabaseReference(**base)


def _cred(**overrides) -> CredentialRequirement:
    """Build a minimal CredentialRequirement with optional overrides."""
    base = {
        "name": "TEST_KEY",
        "type": "api_key",
        "required": True,
        "description": "A test API key.",
        "obtainUrl": "https://test.com/keys",
        "envVar": "TEST_API_KEY",
    }
    base.update(overrides)
    return CredentialRequirement(**base)


def _server(**overrides) -> MCPServerReference:
    """Build a minimal MCPServerReference with optional overrides."""
    base = {
        "name": "life-sciences-test",
        "version": "0.1.0",
        "pypiPackage": "life-sciences-test",
        "description": "Test MCP server.",
        "domain": "Genomics and Sequencing",
        "databases": [_db()],
        "credentials": [],
        "dependencies": [],
    }
    base.update(overrides)
    return MCPServerReference(**base)


def _manifest(
    servers: list[MCPServerReference] | None = None,
    skills: list[SkillReference] | None = None,
    steering_files: list[SteeringFileReference] | None = None,
    pipeline_registries: list[PipelineRegistryReference] | None = None,
) -> BundleManifest:
    """Build a minimal BundleManifest."""
    return BundleManifest(
        name="test-bundle",
        version="1.0.0",
        components=BundleComponents(
            mcpServers=servers or [],
            skills=skills or [],
            steeringFiles=steering_files or [],
            pipelineRegistries=pipeline_registries or [],
        ),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    )


# ---------------------------------------------------------------------------
# compute_resource_status
# ---------------------------------------------------------------------------


class TestComputeResourceStatus:
    """Tests for the compute_resource_status helper."""

    def test_ready_when_installed_and_no_credentials_required(self):
        assert compute_resource_status(
            server_installed=True,
            required_credential_env_vars=[],
            configured_credentials=set(),
        ) == "ready"

    def test_ready_when_installed_and_all_credentials_configured(self):
        assert compute_resource_status(
            server_installed=True,
            required_credential_env_vars=["KEY_A", "KEY_B"],
            configured_credentials={"KEY_A", "KEY_B"},
        ) == "ready"

    def test_needs_credentials_when_installed_but_missing_creds(self):
        assert compute_resource_status(
            server_installed=True,
            required_credential_env_vars=["KEY_A"],
            configured_credentials=set(),
        ) == "needs_credentials"

    def test_needs_credentials_when_partial_creds(self):
        assert compute_resource_status(
            server_installed=True,
            required_credential_env_vars=["KEY_A", "KEY_B"],
            configured_credentials={"KEY_A"},
        ) == "needs_credentials"

    def test_needs_setup_when_not_installed(self):
        assert compute_resource_status(
            server_installed=False,
            required_credential_env_vars=[],
            configured_credentials=set(),
        ) == "needs_setup"

    def test_needs_setup_takes_precedence_over_credentials(self):
        """Even if credentials are configured, not-installed → needs_setup."""
        assert compute_resource_status(
            server_installed=False,
            required_credential_env_vars=["KEY_A"],
            configured_credentials={"KEY_A"},
        ) == "needs_setup"


# ---------------------------------------------------------------------------
# DashboardRenderer.generate — summary
# ---------------------------------------------------------------------------


class TestDashboardSummary:
    """Tests for the summary section of the generated dashboard."""

    def test_empty_manifest_produces_zero_counts(self):
        m = _manifest()
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()
        s = data.summary
        assert s.totalDatabases == 0
        assert s.totalMCPServers == 0
        assert s.totalSkills == 0
        assert s.totalPipelines == 0
        assert s.totalSteeringFiles == 0
        assert s.installedMCPServers == 0
        assert s.configuredCredentials == 0

    def test_counts_databases_across_servers(self):
        s1 = _server(
            name="server-a",
            databases=[_db(name="DB1"), _db(name="DB2")],
        )
        s2 = _server(
            name="server-b",
            databases=[_db(name="DB3")],
        )
        m = _manifest(servers=[s1, s2])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()
        assert data.summary.totalDatabases == 3

    def test_counts_mcp_servers(self):
        m = _manifest(servers=[_server(name="a"), _server(name="b")])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()
        assert data.summary.totalMCPServers == 2

    def test_counts_installed_mcp_servers(self):
        m = _manifest(servers=[_server(name="a"), _server(name="b")])
        renderer = DashboardRenderer(m, {"a"}, set())
        data = renderer.generate()
        assert data.summary.installedMCPServers == 1

    def test_counts_skills(self):
        skills = [
            SkillReference(
                name="Skill A",
                filename="skill-a.md",
                description="A skill.",
                domain="Genomics and Sequencing",
            ),
        ]
        m = _manifest(skills=skills)
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()
        assert data.summary.totalSkills == 1

    def test_counts_steering_files(self):
        sfs = [
            SteeringFileReference(
                name="Guide A",
                filename="guide-a.md",
                description="A guide.",
                domain="Genomics and Sequencing",
            ),
        ]
        m = _manifest(steering_files=sfs)
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()
        assert data.summary.totalSteeringFiles == 1

    def test_counts_pipeline_registries(self):
        prs = [
            PipelineRegistryReference(
                name="nf-core",
                workflowLanguage="Nextflow",
                source="nf-core",
                description="nf-core pipelines.",
            ),
        ]
        m = _manifest(pipeline_registries=prs)
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()
        assert data.summary.totalPipelines == 1

    def test_counts_configured_credentials(self):
        server = _server(
            credentials=[
                _cred(name="Key A", envVar="KEY_A"),
                _cred(name="Key B", envVar="KEY_B"),
            ],
        )
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), {"KEY_A"})
        data = renderer.generate()
        assert data.summary.configuredCredentials == 1


# ---------------------------------------------------------------------------
# DashboardRenderer.generate — categories & resources
# ---------------------------------------------------------------------------


class TestDashboardCategories:
    """Tests for category grouping and resource status."""

    def test_resources_grouped_by_domain(self):
        s1 = _server(name="genomics", domain="Genomics and Sequencing", databases=[_db(name="NCBI")])
        s2 = _server(name="proteomics", domain="Proteomics", databases=[_db(name="UniProt")])
        m = _manifest(servers=[s1, s2])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        cat_names = [c.name for c in data.categories]
        assert ResourceCategory.GENOMICS_AND_SEQUENCING in cat_names
        assert ResourceCategory.PROTEOMICS in cat_names

    def test_category_resource_count_matches(self):
        server = _server(databases=[_db(name="A"), _db(name="B"), _db(name="C")])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        assert len(data.categories) == 1
        cat = data.categories[0]
        assert cat.resourceCount == 3
        assert len(cat.resources) == 3

    def test_resource_status_ready(self):
        server = _server(name="srv", credentials=[])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        data = renderer.generate()

        res = data.categories[0].resources[0]
        assert res.status == "ready"
        assert res.mcpServerInstalled is True

    def test_resource_status_needs_setup(self):
        server = _server(name="srv")
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        res = data.categories[0].resources[0]
        assert res.status == "needs_setup"
        assert res.mcpServerInstalled is False

    def test_resource_status_needs_credentials(self):
        server = _server(
            name="srv",
            credentials=[_cred(envVar="MY_KEY", required=True)],
        )
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        data = renderer.generate()

        res = data.categories[0].resources[0]
        assert res.status == "needs_credentials"
        assert res.credentialInstructions is not None
        assert "MY_KEY" in res.credentialInstructions

    def test_quick_access_command_when_installed(self):
        server = _server(name="srv", pypiPackage="life-sciences-test")
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        data = renderer.generate()

        res = data.categories[0].resources[0]
        assert res.quickAccessCommand == "uvx life-sciences-test"

    def test_no_quick_access_when_not_installed(self):
        server = _server(name="srv")
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        res = data.categories[0].resources[0]
        assert res.quickAccessCommand is None

    def test_skills_appear_in_categories(self):
        skills = [
            SkillReference(
                name="Bio Formats",
                filename="bio-formats.md",
                description="File format skill.",
                domain="Genomics and Sequencing",
            ),
        ]
        m = _manifest(skills=skills)
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        assert len(data.categories) == 1
        res = data.categories[0].resources[0]
        assert res.name == "Bio Formats"
        assert res.status == "ready"

    def test_steering_files_appear_in_categories(self):
        sfs = [
            SteeringFileReference(
                name="Variant Calling",
                filename="variant-calling.md",
                description="Variant calling guide.",
                domain="Genomics and Sequencing",
            ),
        ]
        m = _manifest(steering_files=sfs)
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        assert len(data.categories) == 1
        res = data.categories[0].resources[0]
        assert res.name == "Variant Calling"
        assert res.status == "ready"

    def test_categories_sorted_alphabetically(self):
        s1 = _server(name="z-server", domain="Proteomics", databases=[_db()])
        s2 = _server(name="a-server", domain="Genomics and Sequencing", databases=[_db()])
        m = _manifest(servers=[s1, s2])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        cat_names = [str(c.name) for c in data.categories]
        assert cat_names == sorted(cat_names)

    def test_optional_credentials_do_not_affect_status(self):
        """Non-required credentials should not cause needs_credentials status."""
        server = _server(
            name="srv",
            credentials=[_cred(envVar="OPT_KEY", required=False)],
        )
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        data = renderer.generate()

        res = data.categories[0].resources[0]
        assert res.status == "ready"


# ---------------------------------------------------------------------------
# DashboardRenderer.render_markdown
# ---------------------------------------------------------------------------


class TestRenderMarkdown:
    """Tests for the markdown rendering output."""

    def test_contains_summary_header(self):
        server = _server(databases=[_db(name="NCBI")])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        md = renderer.render_markdown()

        assert "# 🧬 Kiro for Life Sciences — Onboarding Dashboard" in md
        assert "## Summary" in md

    def test_contains_summary_counts(self):
        server = _server(databases=[_db(name="NCBI"), _db(name="Ensembl")])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        md = renderer.render_markdown()

        assert "| Databases | 2 |" in md
        assert "| MCP Servers | 1 |" in md

    def test_contains_category_heading(self):
        server = _server(domain="Genomics and Sequencing", databases=[_db()])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        md = renderer.render_markdown()

        assert "## Genomics and Sequencing (1 resources)" in md

    def test_contains_resource_name(self):
        server = _server(databases=[_db(name="NCBI")])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        md = renderer.render_markdown()

        assert "### NCBI" in md

    def test_ready_status_icon(self):
        server = _server(name="srv", databases=[_db()])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        md = renderer.render_markdown()

        assert "✅ Ready" in md

    def test_needs_setup_status_icon(self):
        server = _server(databases=[_db()])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        md = renderer.render_markdown()

        assert "📦 Needs Setup" in md

    def test_needs_credentials_status_icon(self):
        server = _server(
            name="srv",
            credentials=[_cred(envVar="MY_KEY", required=True)],
            databases=[_db()],
        )
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        md = renderer.render_markdown()

        assert "⚠️ Needs Credentials" in md

    def test_credential_instructions_in_markdown(self):
        server = _server(
            name="srv",
            credentials=[_cred(name="Test Key", envVar="MY_KEY", required=True, obtainUrl="https://example.com/keys")],
            databases=[_db()],
        )
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        md = renderer.render_markdown()

        assert "Credential Setup" in md
        assert "https://example.com/keys" in md
        assert "MY_KEY" in md

    def test_quick_access_in_markdown(self):
        server = _server(name="srv", pypiPackage="life-sciences-genomics")
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, {"srv"}, set())
        md = renderer.render_markdown()

        assert "`uvx life-sciences-genomics`" in md

    def test_empty_manifest_renders_without_error(self):
        m = _manifest()
        renderer = DashboardRenderer(m, set(), set())
        md = renderer.render_markdown()

        assert "# 🧬 Kiro for Life Sciences — Onboarding Dashboard" in md
        assert "| Databases | 0 |" in md


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge-case tests for the dashboard renderer."""

    def test_multiple_servers_same_domain(self):
        """Multiple servers in the same domain should merge into one category."""
        s1 = _server(name="srv-a", domain="Genomics and Sequencing", databases=[_db(name="A")])
        s2 = _server(name="srv-b", domain="Genomics and Sequencing", databases=[_db(name="B")])
        m = _manifest(servers=[s1, s2])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        genomics_cats = [c for c in data.categories if str(c.name) == "Genomics and Sequencing"]
        assert len(genomics_cats) == 1
        assert genomics_cats[0].resourceCount == 2

    def test_server_with_no_databases(self):
        """A server with no databases should not produce resources (but still count as MCP server)."""
        server = _server(name="empty-srv", databases=[])
        m = _manifest(servers=[server])
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        assert data.summary.totalMCPServers == 1
        assert data.summary.totalDatabases == 0
        # No categories from databases, but domain might still appear if skills/steering exist
        db_resources = [
            r for c in data.categories for r in c.resources
        ]
        assert len(db_resources) == 0

    def test_mixed_installed_and_not_installed(self):
        """Dashboard should correctly reflect mixed installation states."""
        s1 = _server(name="installed", databases=[_db(name="A")])
        s2 = _server(name="not-installed", databases=[_db(name="B")])
        m = _manifest(servers=[s1, s2])
        renderer = DashboardRenderer(m, {"installed"}, set())
        data = renderer.generate()

        all_resources = [r for c in data.categories for r in c.resources]
        statuses = {r.name: r.status for r in all_resources}
        assert statuses["A"] == "ready"
        assert statuses["B"] == "needs_setup"

    def test_all_resources_accounted_for(self):
        """Total resources across categories should equal sum of databases + skills + steering files."""
        s1 = _server(name="srv", databases=[_db(name="DB1"), _db(name="DB2")])
        skills = [
            SkillReference(name="Skill1", filename="s1.md", description="S1.", domain="Genomics and Sequencing"),
        ]
        sfs = [
            SteeringFileReference(name="Guide1", filename="g1.md", description="G1.", domain="Proteomics"),
        ]
        m = _manifest(servers=[s1], skills=skills, steering_files=sfs)
        renderer = DashboardRenderer(m, set(), set())
        data = renderer.generate()

        total_resources = sum(c.resourceCount for c in data.categories)
        assert total_resources == 4  # 2 databases + 1 skill + 1 steering file
