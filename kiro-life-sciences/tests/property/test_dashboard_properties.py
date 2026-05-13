"""Property-based tests for the onboarding dashboard.

Uses Hypothesis to verify resource grouping and status computation
properties.  Each test runs a minimum of 100 iterations.
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st

from kiro_life_sciences.models.catalog import ResourceCategory, ResourceEntry
from kiro_life_sciences.dashboard.renderer import (
    DashboardRenderer,
    compute_resource_status,
)
from kiro_life_sciences.models.manifest import (
    BundleComponents,
    BundleManifest,
    CredentialRequirement,
    DatabaseReference,
    MCPServerReference,
    ResourceCatalogDefinition,
)


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_ "),
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip() != "")

_category_st = st.sampled_from(list(ResourceCategory))

_resource_type_st = st.sampled_from(["database", "pipeline", "tool", "skill", "steering_file"])

_status_st = st.sampled_from(["ready", "needs_setup", "needs_credentials"])

_domain_st = st.sampled_from([
    "Genomics and Sequencing", "Proteomics", "Structural Biology",
    "Clinical and Pharma", "Pipelines", "Ontologies",
])


@st.composite
def resource_entry_st(draw, entry_id=None, category=None):
    """Generate a valid ResourceEntry."""
    eid = entry_id or f"entry-{draw(st.integers(min_value=0, max_value=99999))}"
    cat = category or draw(_category_st)
    return ResourceEntry(
        id=eid,
        name=draw(_name_st),
        description=draw(_name_st),
        category=cat,
        resourceType=draw(_resource_type_st),
        url="https://example.com/" + eid,
        authRequired=draw(st.booleans()),
        dataFormats=[],
        usageInstructions=draw(_name_st),
        status=draw(_status_st),
    )


# ===========================================================================
# Property 7: Resource Grouping Invariant (Task 4.2)
# ===========================================================================
# Feature: kiro-life-sciences, Property 7: Resource Grouping Invariant


@st.composite
def manifest_with_servers_st(draw):
    """Generate a manifest with MCP servers that have databases, producing
    resources for the dashboard to group."""
    num_servers = draw(st.integers(min_value=1, max_value=5))
    servers = []
    for i in range(num_servers):
        domain = draw(_domain_st)
        num_dbs = draw(st.integers(min_value=1, max_value=3))
        databases = []
        for j in range(num_dbs):
            databases.append(DatabaseReference(
                name=f"DB-{i}-{j}",
                description=f"Database {i}-{j}",
                apiBaseUrl=f"https://api-{i}-{j}.example.com",
                authRequired=draw(st.booleans()),
                url=f"https://db-{i}-{j}.example.com",
            ))
        servers.append(MCPServerReference(
            name=f"server-{i}",
            version="1.0.0",
            pypiPackage=f"server-{i}",
            description=f"Server {i}",
            domain=domain,
            databases=databases,
            credentials=[],
        ))

    manifest = BundleManifest(
        name="test-bundle",
        version="1.0.0",
        components=BundleComponents(mcpServers=servers),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    )
    return manifest


class TestResourceGroupingInvariant:
    """Grouping by category: every resource appears in exactly one group,
    no resources lost, each group count matches actual members.

    **Validates: Requirements 6.2, 6.3, 9.1**
    """

    @given(manifest=manifest_with_servers_st())
    @settings(max_examples=100)
    def test_grouping_invariant(self, manifest: BundleManifest):
        renderer = DashboardRenderer(
            manifest=manifest,
            installed_servers=set(),
            configured_credentials=set(),
        )
        data = renderer.generate()

        # Count total resources across all categories
        total_resources = 0
        all_resource_names = []
        for cat in data.categories:
            assert cat.resourceCount == len(cat.resources), (
                f"Category {cat.name}: reported count {cat.resourceCount} "
                f"!= actual {len(cat.resources)}"
            )
            total_resources += cat.resourceCount
            for res in cat.resources:
                all_resource_names.append(res.name)

        # Total databases in manifest
        expected_db_count = sum(
            len(s.databases) for s in manifest.components.mcpServers
        )
        assert total_resources == expected_db_count, (
            f"Total grouped resources {total_resources} != "
            f"expected {expected_db_count}"
        )

        # No resource appears in more than one group
        assert len(all_resource_names) == len(set(all_resource_names)), (
            "Some resources appear in multiple groups"
        )


# ===========================================================================
# Property 8: Resource Status Computation (Task 4.3)
# ===========================================================================
# Feature: kiro-life-sciences, Property 8: Resource Status Computation


@st.composite
def status_input_st(draw):
    """Generate random (installed, required_creds, configured_creds) combos."""
    installed = draw(st.booleans())
    num_required = draw(st.integers(min_value=0, max_value=5))
    required_vars = [f"CRED_{i}" for i in range(num_required)]
    # Randomly configure some subset of the required credentials
    configured = set()
    for var in required_vars:
        if draw(st.booleans()):
            configured.add(var)
    return installed, required_vars, configured


class TestResourceStatusComputation:
    """Status is ``ready`` if installed + all creds configured,
    ``needs_credentials`` if installed but missing creds,
    ``needs_setup`` if not installed.

    **Validates: Requirements 6.4**
    """

    @given(data=status_input_st())
    @settings(max_examples=100)
    def test_status_computation(self, data):
        installed, required_vars, configured = data
        status = compute_resource_status(
            server_installed=installed,
            required_credential_env_vars=required_vars,
            configured_credentials=configured,
        )

        if not installed:
            assert status == "needs_setup"
        elif required_vars:
            missing = [v for v in required_vars if v not in configured]
            if missing:
                assert status == "needs_credentials"
            else:
                assert status == "ready"
        else:
            assert status == "ready"
