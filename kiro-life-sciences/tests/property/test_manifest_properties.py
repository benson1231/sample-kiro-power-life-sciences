"""Property-based tests for the bundle manifest, dependency resolver, installer, and updater.

Uses Hypothesis to verify universal correctness properties across randomly
generated inputs.  Each test runs a minimum of 100 iterations.
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st, assume

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
from kiro_life_sciences.installer.dependency_resolver import (
    DependencyResolver,
)
from kiro_life_sciences.installer.installer import (
    BundleInstaller,
    ComponentInstaller,
    InstallationResult,
)
from kiro_life_sciences.installer.updater import ManifestUpdater


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Pd"), whitelist_characters="-_ "),
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip() != "")

_version_st = st.builds(
    lambda ma, mi, pa: f"{ma}.{mi}.{pa}",
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
)

_domain_st = st.sampled_from([
    "Genomics and Sequencing", "Proteomics", "Structural Biology",
    "Clinical and Pharma", "Pipelines", "Ontologies",
])

_workflow_lang_st = st.sampled_from(["Nextflow", "WDL", "CWL", "mixed"])
_cred_type_st = st.sampled_from(["api_key", "oauth", "username_password"])


@st.composite
def credential_requirements_st(draw):
    """Generate a valid CredentialRequirement."""
    return CredentialRequirement(
        name=draw(_name_st),
        type=draw(_cred_type_st),
        required=draw(st.booleans()),
        description=draw(_name_st),
        obtainUrl="https://example.com/" + draw(_name_st).replace(" ", ""),
        envVar="ENV_" + draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=8)),
    )


@st.composite
def database_reference_st(draw):
    """Generate a valid DatabaseReference."""
    return DatabaseReference(
        name=draw(_name_st),
        description=draw(_name_st),
        apiBaseUrl="https://api.example.com/" + draw(_name_st).replace(" ", ""),
        authRequired=draw(st.booleans()),
        url="https://example.com/" + draw(_name_st).replace(" ", ""),
        dataFormats=draw(st.lists(st.sampled_from(["FASTA", "JSON", "XML", "CSV"]), max_size=3)),
        exampleQueries=draw(st.lists(_name_st, max_size=2)),
    )


@st.composite
def power_reference_st(draw):
    """Generate a valid PowerReference."""
    return PowerReference(
        name=draw(_name_st),
        version=draw(_version_st),
        required=draw(st.booleans()),
        description=draw(_name_st),
    )


@st.composite
def skill_reference_st(draw):
    """Generate a valid SkillReference."""
    return SkillReference(
        name=draw(_name_st),
        filename=draw(_name_st).replace(" ", "-") + ".md",
        description=draw(_name_st),
        domain=draw(_domain_st),
    )


@st.composite
def steering_file_reference_st(draw):
    """Generate a valid SteeringFileReference."""
    return SteeringFileReference(
        name=draw(_name_st),
        filename=draw(_name_st).replace(" ", "-") + ".md",
        description=draw(_name_st),
        domain=draw(_domain_st),
    )


@st.composite
def pipeline_registry_reference_st(draw):
    """Generate a valid PipelineRegistryReference."""
    return PipelineRegistryReference(
        name=draw(_name_st),
        workflowLanguage=draw(_workflow_lang_st),
        source=draw(_name_st),
        description=draw(_name_st),
    )


@st.composite
def mcp_server_reference_st(draw, name=None, deps=None):
    """Generate a valid MCPServerReference with optional fixed name/deps."""
    server_name = name or draw(_name_st)
    return MCPServerReference(
        name=server_name,
        version=draw(_version_st),
        pypiPackage=server_name.lower().replace(" ", "-"),
        description=draw(_name_st),
        domain=draw(_domain_st),
        databases=draw(st.lists(database_reference_st(), max_size=2)),
        credentials=draw(st.lists(credential_requirements_st(), max_size=2)),
        dependencies=deps if deps is not None else [],
    )


@st.composite
def bundle_manifest_st(draw):
    """Generate a valid BundleManifest with random components."""
    powers = draw(st.lists(power_reference_st(), max_size=3))
    skills = draw(st.lists(skill_reference_st(), max_size=4))
    steering = draw(st.lists(steering_file_reference_st(), max_size=4))
    pipelines = draw(st.lists(pipeline_registry_reference_st(), max_size=3))

    # Generate MCP servers with unique names and no dependencies (for basic manifest)
    num_servers = draw(st.integers(min_value=0, max_value=5))
    server_names = [f"server-{i}" for i in range(num_servers)]
    servers = []
    for sn in server_names:
        servers.append(draw(mcp_server_reference_st(name=sn, deps=[])))

    return BundleManifest(
        name=draw(_name_st),
        version=draw(_version_st),
        description=draw(_name_st),
        components=BundleComponents(
            powers=powers,
            mcpServers=servers,
            skills=skills,
            steeringFiles=steering,
            pipelineRegistries=pipelines,
        ),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    )


# ===========================================================================
# Property 1: Manifest Schema Validation Round-Trip (Task 3.2)
# ===========================================================================
# Feature: kiro-life-sciences, Property 1: Manifest Schema Validation Round-Trip


class TestManifestRoundTrip:
    """For any valid BundleManifest, serializing to JSON and parsing back
    produces an equivalent object.  Every component must have all required
    fields.

    **Validates: Requirements 1.1, 1.2, 1.3, 4.1, 8.2, 8.3, 8.4, 8.5**
    """

    @given(manifest=bundle_manifest_st())
    @settings(max_examples=100)
    def test_json_round_trip(self, manifest: BundleManifest):
        """Serializing to JSON and parsing back yields an equivalent object."""
        json_str = manifest.model_dump_json()
        restored = BundleManifest.model_validate_json(json_str)
        assert restored == manifest

    @given(manifest=bundle_manifest_st())
    @settings(max_examples=100)
    def test_all_components_have_required_fields(self, manifest: BundleManifest):
        """Every component has all required fields (name, version/filename, description)."""
        for power in manifest.components.powers:
            assert len(power.name) >= 1
            assert len(power.version) >= 1
            assert len(power.description) >= 1

        for server in manifest.components.mcpServers:
            assert len(server.name) >= 1
            assert len(server.version) >= 1
            assert len(server.description) >= 1
            assert len(server.pypiPackage) >= 1
            assert len(server.domain) >= 1
            for db in server.databases:
                assert len(db.name) >= 1
                assert len(db.apiBaseUrl) >= 1

        for skill in manifest.components.skills:
            assert len(skill.name) >= 1
            assert len(skill.filename) >= 1
            assert len(skill.description) >= 1

        for sf in manifest.components.steeringFiles:
            assert len(sf.name) >= 1
            assert len(sf.filename) >= 1
            assert len(sf.description) >= 1

        for pr in manifest.components.pipelineRegistries:
            assert len(pr.name) >= 1
            assert len(pr.description) >= 1


# ===========================================================================
# Property 2: Dependency Conflict Detection (Task 3.3)
# ===========================================================================
# Feature: kiro-life-sciences, Property 2: Dependency Conflict Detection


@st.composite
def manifest_with_conflicts_st(draw):
    """Generate a manifest with duplicate server names having different versions."""
    base_name = "conflict-server"
    v1 = draw(_version_st)
    v2 = draw(_version_st)
    assume(v1 != v2)

    server1 = draw(mcp_server_reference_st(name=base_name, deps=[]))
    # Override version on server1
    server1 = server1.model_copy(update={"version": v1})
    server2 = draw(mcp_server_reference_st(name=base_name, deps=[]))
    server2 = server2.model_copy(update={"version": v2})

    # Add some non-conflicting servers
    extra_servers = draw(st.lists(
        mcp_server_reference_st(name=None, deps=[]),
        min_size=0,
        max_size=3,
    ))
    # Ensure extra servers don't share the conflict name
    extra_servers = [s for s in extra_servers if s.name != base_name]

    all_servers = [server1, server2] + extra_servers

    return BundleManifest(
        name="test-bundle",
        version="1.0.0",
        components=BundleComponents(mcpServers=all_servers),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    ), base_name


class TestDependencyConflictDetection:
    """For any manifest with duplicate server names having different versions,
    detect_conflicts returns all conflicting names.

    **Validates: Requirements 1.4**
    """

    @given(data=manifest_with_conflicts_st())
    @settings(max_examples=100)
    def test_conflicts_detected(self, data):
        manifest, conflict_name = data
        resolver = DependencyResolver()
        conflicts = resolver.detect_conflicts(manifest)

        conflict_names = {c.dependency for c in conflicts}
        assert conflict_name in conflict_names

        for conflict in conflicts:
            if conflict.dependency == conflict_name:
                # At least 2 different versions
                assert len(set(conflict.required_by.values())) >= 2


# ===========================================================================
# Property 3: Dependency Resolution Produces Valid Install Order (Task 3.4)
# ===========================================================================
# Feature: kiro-life-sciences, Property 3: Dependency Resolution Install Order


@st.composite
def acyclic_dependency_manifest_st(draw):
    """Generate a manifest with a valid (acyclic) dependency graph.

    Builds a DAG by assigning each server an index and only allowing
    dependencies on servers with a lower index.
    """
    num_servers = draw(st.integers(min_value=1, max_value=8))
    server_names = [f"srv-{i}" for i in range(num_servers)]

    servers = []
    for i, name in enumerate(server_names):
        # Can only depend on servers with lower index (ensures acyclic)
        possible_deps = server_names[:i]
        deps = draw(st.lists(
            st.sampled_from(possible_deps) if possible_deps else st.nothing(),
            max_size=min(3, len(possible_deps)),
            unique=True,
        ))
        servers.append(draw(mcp_server_reference_st(name=name, deps=deps)))

    return BundleManifest(
        name="test-bundle",
        version="1.0.0",
        components=BundleComponents(mcpServers=servers),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    )


class TestDependencyResolutionOrder:
    """For any valid (acyclic) dependency graph, the resolver produces an order
    where every dependency appears before its dependent, and every component
    appears exactly once.

    **Validates: Requirements 2.1**
    """

    @given(manifest=acyclic_dependency_manifest_st())
    @settings(max_examples=100)
    def test_valid_install_order(self, manifest: BundleManifest):
        resolver = DependencyResolver()
        order = resolver.resolve(manifest)

        server_names = {s.name for s in manifest.components.mcpServers}
        # Every declared server appears in the order
        for name in server_names:
            assert name in order

        # No duplicates
        assert len(order) == len(set(order))

        # Every dependency appears before its dependent
        position = {name: idx for idx, name in enumerate(order)}
        for server in manifest.components.mcpServers:
            for dep in server.dependencies:
                assert position[dep] < position[server.name], (
                    f"{dep} should appear before {server.name}"
                )


# ===========================================================================
# Property 4: Component Count Invariant (Task 3.5)
# ===========================================================================
# Feature: kiro-life-sciences, Property 4: Component Count Invariant


class _TrackingInstaller:
    """A ComponentInstaller that can be configured to fail on specific components."""

    def __init__(self, failing_components: set[str]):
        self._failing = failing_components

    def install_power(self, name: str, version: str) -> None:
        if name in self._failing:
            raise RuntimeError(f"Simulated failure: {name}")

    def install_mcp_server(self, name: str, version: str) -> None:
        if name in self._failing:
            raise RuntimeError(f"Simulated failure: {name}")

    def install_skill(self, name: str, filename: str) -> None:
        if name in self._failing:
            raise RuntimeError(f"Simulated failure: {name}")

    def install_steering_file(self, name: str, filename: str) -> None:
        if name in self._failing:
            raise RuntimeError(f"Simulated failure: {name}")

    def install_pipeline_registry(self, name: str) -> None:
        if name in self._failing:
            raise RuntimeError(f"Simulated failure: {name}")


@st.composite
def manifest_with_failures_st(draw):
    """Generate a manifest and a random subset of component names that will fail."""
    manifest = draw(bundle_manifest_st())

    all_names = set()
    for p in manifest.components.powers:
        all_names.add(p.name)
    for s in manifest.components.mcpServers:
        all_names.add(s.name)
    for sk in manifest.components.skills:
        all_names.add(sk.name)
    for sf in manifest.components.steeringFiles:
        all_names.add(sf.name)
    for pr in manifest.components.pipelineRegistries:
        all_names.add(pr.name)

    failing = draw(st.frozensets(st.sampled_from(sorted(all_names)) if all_names else st.nothing()))
    return manifest, failing


class TestComponentCountInvariant:
    """The reported counts equal the number of each component type in the
    manifest minus failures.

    **Validates: Requirements 2.3, 6.8**
    """

    @given(data=manifest_with_failures_st())
    @settings(max_examples=100)
    def test_counts_match(self, data):
        manifest, failing = data
        installer = BundleInstaller(_TrackingInstaller(failing))
        result = installer.install(manifest)

        # Expected counts per type
        expected_powers = sum(1 for p in manifest.components.powers if p.name not in failing)
        expected_servers = sum(1 for s in manifest.components.mcpServers if s.name not in failing)
        expected_skills = sum(1 for s in manifest.components.skills if s.name not in failing)
        expected_steering = sum(1 for s in manifest.components.steeringFiles if s.name not in failing)
        expected_pipelines = sum(1 for p in manifest.components.pipelineRegistries if p.name not in failing)

        assert result.installed_powers == expected_powers
        assert result.installed_mcp_servers == expected_servers
        assert result.installed_skills == expected_skills
        assert result.installed_steering_files == expected_steering
        assert result.installed_pipeline_registries == expected_pipelines

        # Total installed + failures == total components
        total_components = (
            len(manifest.components.powers)
            + len(manifest.components.mcpServers)
            + len(manifest.components.skills)
            + len(manifest.components.steeringFiles)
            + len(manifest.components.pipelineRegistries)
        )
        assert result.total_installed + len(result.failures) == total_components


# ===========================================================================
# Property 5: Installation Graceful Failure Handling (Task 3.6)
# ===========================================================================
# Feature: kiro-life-sciences, Property 5: Installation Graceful Failure


class TestInstallationGracefulFailure:
    """For any manifest and any subset of failing components, the installer
    continues, reports each failure, and produces a summary.

    **Validates: Requirements 2.4, 2.5**
    """

    @given(data=manifest_with_failures_st())
    @settings(max_examples=100)
    def test_graceful_failure(self, data):
        manifest, failing = data
        installer = BundleInstaller(_TrackingInstaller(failing))
        result = installer.install(manifest)

        # Every failure is reported with name and reason
        failed_names = {f.component_name for f in result.failures}
        for name in failing:
            # Only names that are actually in the manifest should appear
            all_component_names = set()
            for p in manifest.components.powers:
                all_component_names.add(p.name)
            for s in manifest.components.mcpServers:
                all_component_names.add(s.name)
            for sk in manifest.components.skills:
                all_component_names.add(sk.name)
            for sf in manifest.components.steeringFiles:
                all_component_names.add(sf.name)
            for pr in manifest.components.pipelineRegistries:
                all_component_names.add(pr.name)

            if name in all_component_names:
                assert name in failed_names, f"Expected {name} in failures"

        # Each failure has a non-empty reason
        for failure in result.failures:
            assert len(failure.reason) > 0
            assert len(failure.component_name) > 0
            assert len(failure.component_type) > 0

        # Non-failing components are still installed
        non_failing_count = (
            sum(1 for p in manifest.components.powers if p.name not in failing)
            + sum(1 for s in manifest.components.mcpServers if s.name not in failing)
            + sum(1 for s in manifest.components.skills if s.name not in failing)
            + sum(1 for s in manifest.components.steeringFiles if s.name not in failing)
            + sum(1 for p in manifest.components.pipelineRegistries if p.name not in failing)
        )
        assert result.total_installed == non_failing_count


# ===========================================================================
# Property 6: Manifest Diff Correctness (Task 3.7)
# ===========================================================================
# Feature: kiro-life-sciences, Property 6: Manifest Diff Correctness


@st.composite
def manifest_pair_st(draw):
    """Generate two manifests (V1 and V2) with random changes."""
    # Build V1
    num_powers = draw(st.integers(min_value=0, max_value=3))
    num_servers = draw(st.integers(min_value=0, max_value=4))
    num_skills = draw(st.integers(min_value=0, max_value=3))
    num_steering = draw(st.integers(min_value=0, max_value=3))
    num_pipelines = draw(st.integers(min_value=0, max_value=3))

    v1_powers = {}
    for i in range(num_powers):
        name = f"power-{i}"
        v1_powers[name] = draw(_version_st)

    v1_servers = {}
    for i in range(num_servers):
        name = f"server-{i}"
        v1_servers[name] = draw(_version_st)

    v1_skills = {}
    for i in range(num_skills):
        name = f"skill-{i}"
        v1_skills[name] = f"skill-{i}.md"

    v1_steering = {}
    for i in range(num_steering):
        name = f"steering-{i}"
        v1_steering[name] = f"steering-{i}.md"

    v1_pipelines = set()
    for i in range(num_pipelines):
        v1_pipelines.add(f"pipeline-{i}")

    # Build V2 by randomly modifying V1
    v2_powers = dict(v1_powers)
    v2_servers = dict(v1_servers)
    v2_skills = dict(v1_skills)
    v2_steering = dict(v1_steering)
    v2_pipelines = set(v1_pipelines)

    # Randomly add/remove/update powers
    if v2_powers and draw(st.booleans()):
        key = draw(st.sampled_from(sorted(v2_powers.keys())))
        v2_powers[key] = draw(_version_st)
    if draw(st.booleans()):
        new_name = f"power-new-{draw(st.integers(min_value=100, max_value=999))}"
        v2_powers[new_name] = draw(_version_st)
    if v2_powers and draw(st.booleans()):
        key = draw(st.sampled_from(sorted(v2_powers.keys())))
        del v2_powers[key]

    # Randomly add/remove/update servers
    if v2_servers and draw(st.booleans()):
        key = draw(st.sampled_from(sorted(v2_servers.keys())))
        v2_servers[key] = draw(_version_st)
    if draw(st.booleans()):
        new_name = f"server-new-{draw(st.integers(min_value=100, max_value=999))}"
        v2_servers[new_name] = draw(_version_st)
    if v2_servers and draw(st.booleans()):
        key = draw(st.sampled_from(sorted(v2_servers.keys())))
        del v2_servers[key]

    # Build actual manifest objects
    def _make_manifest(powers, servers, skills, steering, pipelines, ver):
        return BundleManifest(
            name="test-bundle",
            version=ver,
            components=BundleComponents(
                powers=[
                    PowerReference(name=n, version=v, required=True, description="p")
                    for n, v in sorted(powers.items())
                ],
                mcpServers=[
                    MCPServerReference(
                        name=n, version=v, pypiPackage=n,
                        description="s", domain="Genomics and Sequencing",
                    )
                    for n, v in sorted(servers.items())
                ],
                skills=[
                    SkillReference(name=n, filename=f, description="sk", domain="General")
                    for n, f in sorted(skills.items())
                ],
                steeringFiles=[
                    SteeringFileReference(name=n, filename=f, description="sf", domain="General")
                    for n, f in sorted(steering.items())
                ],
                pipelineRegistries=[
                    PipelineRegistryReference(
                        name=n, workflowLanguage="Nextflow", source="test", description="pr"
                    )
                    for n in sorted(pipelines)
                ],
            ),
            resourceCatalog=ResourceCatalogDefinition(entries=[]),
        )

    m1 = _make_manifest(v1_powers, v1_servers, v1_skills, v1_steering, v1_pipelines, "1.0.0")
    m2 = _make_manifest(v2_powers, v2_servers, v2_skills, v2_steering, v2_pipelines, "2.0.0")

    return m1, m2, v1_powers, v2_powers, v1_servers, v2_servers


class TestManifestDiffCorrectness:
    """For any two manifests V1 and V2, the diff contains exactly the changed
    components, and major version increases are flagged as breaking.

    **Validates: Requirements 4.3, 4.4**
    """

    @given(data=manifest_pair_st())
    @settings(max_examples=100)
    def test_diff_contains_exactly_changed_components(self, data):
        m1, m2, v1_powers, v2_powers, v1_servers, v2_servers = data
        updater = ManifestUpdater()
        diff = updater.diff(m1, m2)

        # Check powers: every changed power should be in the diff
        all_power_names = set(v1_powers) | set(v2_powers)
        for name in all_power_names:
            old_ver = v1_powers.get(name)
            new_ver = v2_powers.get(name)
            if old_ver != new_ver:
                assert any(
                    c.name == name and c.component_type == "power"
                    for c in diff.changes
                ), f"Power {name} changed but not in diff"
            else:
                assert not any(
                    c.name == name and c.component_type == "power"
                    for c in diff.changes
                ), f"Power {name} unchanged but in diff"

        # Check servers: every changed server should be in the diff
        all_server_names = set(v1_servers) | set(v2_servers)
        for name in all_server_names:
            old_ver = v1_servers.get(name)
            new_ver = v2_servers.get(name)
            if old_ver != new_ver:
                assert any(
                    c.name == name and c.component_type == "mcp_server"
                    for c in diff.changes
                ), f"Server {name} changed but not in diff"
            else:
                assert not any(
                    c.name == name and c.component_type == "mcp_server"
                    for c in diff.changes
                ), f"Server {name} unchanged but in diff"

    @given(data=manifest_pair_st())
    @settings(max_examples=100)
    def test_major_version_increase_flagged_as_breaking(self, data):
        m1, m2, v1_powers, v2_powers, v1_servers, v2_servers = data
        updater = ManifestUpdater()
        diff = updater.diff(m1, m2)

        for change in diff.changes:
            if (
                change.old_version is not None
                and change.new_version is not None
                and change.change_type == "updated"
            ):
                old_major = int(change.old_version.split(".")[0])
                new_major = int(change.new_version.split(".")[0])
                if new_major > old_major:
                    assert change.is_breaking, (
                        f"{change.name}: {change.old_version} -> {change.new_version} "
                        f"should be flagged as breaking"
                    )
