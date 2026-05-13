"""Unit tests for the bundle installer module."""

from __future__ import annotations

import pytest

from kiro_life_sciences.installer.installer import (
    BundleInstaller,
    ComponentInstaller,
    InstallationFailure,
    InstallationResult,
)
from kiro_life_sciences.models.manifest import (
    BundleComponents,
    BundleManifest,
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


def _server(
    name: str,
    version: str = "1.0.0",
    dependencies: list[str] | None = None,
) -> MCPServerReference:
    return MCPServerReference(
        name=name,
        version=version,
        pypiPackage=name,
        description=f"Test server {name}",
        domain="Test",
        dependencies=dependencies or [],
    )


def _power(name: str = "test-power", version: str = "1.0.0") -> PowerReference:
    return PowerReference(
        name=name,
        version=version,
        required=True,
        description=f"Test power {name}",
    )


def _skill(name: str = "test-skill", filename: str = "test.md") -> SkillReference:
    return SkillReference(
        name=name,
        filename=filename,
        description=f"Test skill {name}",
        domain="Test",
    )


def _steering(
    name: str = "test-steering", filename: str = "steering.md"
) -> SteeringFileReference:
    return SteeringFileReference(
        name=name,
        filename=filename,
        description=f"Test steering {name}",
        domain="Test",
    )


def _pipeline(name: str = "test-pipeline") -> PipelineRegistryReference:
    return PipelineRegistryReference(
        name=name,
        workflowLanguage="WDL",
        source="test",
        description=f"Test pipeline {name}",
    )


def _manifest(
    powers: list[PowerReference] | None = None,
    servers: list[MCPServerReference] | None = None,
    skills: list[SkillReference] | None = None,
    steering_files: list[SteeringFileReference] | None = None,
    pipeline_registries: list[PipelineRegistryReference] | None = None,
) -> BundleManifest:
    return BundleManifest(
        name="test-bundle",
        version="1.0.0",
        description="Test bundle",
        components=BundleComponents(
            powers=powers or [],
            mcpServers=servers or [],
            skills=skills or [],
            steeringFiles=steering_files or [],
            pipelineRegistries=pipeline_registries or [],
        ),
        resourceCatalog=ResourceCatalogDefinition(),
    )


class RecordingInstaller:
    """A test double that records every install call and can be told to fail."""

    def __init__(self, fail_on: set[str] | None = None) -> None:
        self.calls: list[tuple[str, str, ...]] = []
        self._fail_on = fail_on or set()

    def _maybe_fail(self, name: str) -> None:
        if name in self._fail_on:
            raise RuntimeError(f"Simulated failure for {name}")

    def install_power(self, name: str, version: str) -> None:
        self._maybe_fail(name)
        self.calls.append(("power", name, version))

    def install_mcp_server(self, name: str, version: str) -> None:
        self._maybe_fail(name)
        self.calls.append(("mcp_server", name, version))

    def install_skill(self, name: str, filename: str) -> None:
        self._maybe_fail(name)
        self.calls.append(("skill", name, filename))

    def install_steering_file(self, name: str, filename: str) -> None:
        self._maybe_fail(name)
        self.calls.append(("steering_file", name, filename))

    def install_pipeline_registry(self, name: str) -> None:
        self._maybe_fail(name)
        self.calls.append(("pipeline_registry", name))


# ---------------------------------------------------------------------------
# InstallationResult data class
# ---------------------------------------------------------------------------


class TestInstallationResult:
    """Tests for the InstallationResult data class."""

    def test_defaults(self) -> None:
        result = InstallationResult()
        assert result.installed_powers == 0
        assert result.installed_mcp_servers == 0
        assert result.installed_skills == 0
        assert result.installed_steering_files == 0
        assert result.installed_pipeline_registries == 0
        assert result.failures == []

    def test_success_when_no_failures(self) -> None:
        result = InstallationResult(installed_powers=1)
        assert result.success is True

    def test_not_success_when_failures_exist(self) -> None:
        result = InstallationResult(
            failures=[
                InstallationFailure(
                    component_name="x", component_type="power", reason="boom"
                )
            ]
        )
        assert result.success is False

    def test_total_installed(self) -> None:
        result = InstallationResult(
            installed_powers=1,
            installed_mcp_servers=2,
            installed_skills=3,
            installed_steering_files=4,
            installed_pipeline_registries=5,
        )
        assert result.total_installed == 15


# ---------------------------------------------------------------------------
# InstallationFailure data class
# ---------------------------------------------------------------------------


class TestInstallationFailure:
    """Tests for the InstallationFailure data class."""

    def test_fields(self) -> None:
        f = InstallationFailure(
            component_name="srv", component_type="mcp_server", reason="timeout"
        )
        assert f.component_name == "srv"
        assert f.component_type == "mcp_server"
        assert f.reason == "timeout"

    def test_frozen(self) -> None:
        f = InstallationFailure(
            component_name="a", component_type="power", reason="err"
        )
        with pytest.raises(AttributeError):
            f.component_name = "b"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ComponentInstaller protocol
# ---------------------------------------------------------------------------


class TestComponentInstallerProtocol:
    """Tests that RecordingInstaller satisfies the ComponentInstaller protocol."""

    def test_recording_installer_is_component_installer(self) -> None:
        assert isinstance(RecordingInstaller(), ComponentInstaller)


# ---------------------------------------------------------------------------
# BundleInstaller — empty manifest
# ---------------------------------------------------------------------------


class TestInstallEmptyManifest:
    """Installing an empty manifest should succeed with zero counts."""

    def test_empty_manifest(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)
        result = installer.install(_manifest())

        assert result.success is True
        assert result.total_installed == 0
        assert result.failures == []
        assert rec.calls == []


# ---------------------------------------------------------------------------
# BundleInstaller — successful installation
# ---------------------------------------------------------------------------


class TestInstallAllComponentTypes:
    """All component types are installed and counted correctly."""

    def test_all_types_installed(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            powers=[_power("p1")],
            servers=[_server("s1"), _server("s2")],
            skills=[_skill("sk1")],
            steering_files=[_steering("st1"), _steering("st2"), _steering("st3")],
            pipeline_registries=[_pipeline("pl1")],
        )
        result = installer.install(manifest)

        assert result.success is True
        assert result.installed_powers == 1
        assert result.installed_mcp_servers == 2
        assert result.installed_skills == 1
        assert result.installed_steering_files == 3
        assert result.installed_pipeline_registries == 1
        assert result.total_installed == 8

    def test_install_calls_recorded(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            powers=[_power("p1")],
            servers=[_server("s1")],
            skills=[_skill("sk1", "sk1.md")],
            steering_files=[_steering("st1", "st1.md")],
            pipeline_registries=[_pipeline("pl1")],
        )
        installer.install(manifest)

        call_types = [c[0] for c in rec.calls]
        assert "power" in call_types
        assert "mcp_server" in call_types
        assert "skill" in call_types
        assert "steering_file" in call_types
        assert "pipeline_registry" in call_types


# ---------------------------------------------------------------------------
# BundleInstaller — MCP server dependency ordering
# ---------------------------------------------------------------------------


class TestMCPServerDependencyOrder:
    """MCP servers are installed in dependency-resolved order."""

    def test_dependency_order_respected(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            servers=[
                _server("A", dependencies=["B"]),
                _server("B", dependencies=["C"]),
                _server("C"),
            ]
        )
        result = installer.install(manifest)

        assert result.success is True
        server_calls = [c[1] for c in rec.calls if c[0] == "mcp_server"]
        assert server_calls.index("C") < server_calls.index("B")
        assert server_calls.index("B") < server_calls.index("A")


# ---------------------------------------------------------------------------
# BundleInstaller — graceful failure handling
# ---------------------------------------------------------------------------


class TestGracefulFailureHandling:
    """Failures are recorded and installation continues."""

    def test_single_power_failure(self) -> None:
        rec = RecordingInstaller(fail_on={"bad-power"})
        installer = BundleInstaller(rec)

        manifest = _manifest(powers=[_power("good-power"), _power("bad-power")])
        result = installer.install(manifest)

        assert result.success is False
        assert result.installed_powers == 1
        assert len(result.failures) == 1
        assert result.failures[0].component_name == "bad-power"
        assert result.failures[0].component_type == "power"
        assert "Simulated failure" in result.failures[0].reason

    def test_single_mcp_server_failure(self) -> None:
        rec = RecordingInstaller(fail_on={"bad-server"})
        installer = BundleInstaller(rec)

        manifest = _manifest(
            servers=[_server("good-server"), _server("bad-server")]
        )
        result = installer.install(manifest)

        assert result.installed_mcp_servers == 1
        assert len(result.failures) == 1
        assert result.failures[0].component_name == "bad-server"
        assert result.failures[0].component_type == "mcp_server"

    def test_single_skill_failure(self) -> None:
        rec = RecordingInstaller(fail_on={"bad-skill"})
        installer = BundleInstaller(rec)

        manifest = _manifest(skills=[_skill("good-skill"), _skill("bad-skill")])
        result = installer.install(manifest)

        assert result.installed_skills == 1
        assert len(result.failures) == 1
        assert result.failures[0].component_type == "skill"

    def test_single_steering_file_failure(self) -> None:
        rec = RecordingInstaller(fail_on={"bad-sf"})
        installer = BundleInstaller(rec)

        manifest = _manifest(
            steering_files=[_steering("good-sf"), _steering("bad-sf")]
        )
        result = installer.install(manifest)

        assert result.installed_steering_files == 1
        assert len(result.failures) == 1
        assert result.failures[0].component_type == "steering_file"

    def test_single_pipeline_registry_failure(self) -> None:
        rec = RecordingInstaller(fail_on={"bad-pl"})
        installer = BundleInstaller(rec)

        manifest = _manifest(
            pipeline_registries=[_pipeline("good-pl"), _pipeline("bad-pl")]
        )
        result = installer.install(manifest)

        assert result.installed_pipeline_registries == 1
        assert len(result.failures) == 1
        assert result.failures[0].component_type == "pipeline_registry"

    def test_multiple_failures_across_types(self) -> None:
        rec = RecordingInstaller(fail_on={"bad-power", "bad-server", "bad-skill"})
        installer = BundleInstaller(rec)

        manifest = _manifest(
            powers=[_power("good-power"), _power("bad-power")],
            servers=[_server("good-server"), _server("bad-server")],
            skills=[_skill("good-skill"), _skill("bad-skill")],
        )
        result = installer.install(manifest)

        assert result.success is False
        assert result.installed_powers == 1
        assert result.installed_mcp_servers == 1
        assert result.installed_skills == 1
        assert len(result.failures) == 3
        failed_names = {f.component_name for f in result.failures}
        assert failed_names == {"bad-power", "bad-server", "bad-skill"}

    def test_all_components_fail(self) -> None:
        rec = RecordingInstaller(fail_on={"p1", "s1", "sk1", "st1", "pl1"})
        installer = BundleInstaller(rec)

        manifest = _manifest(
            powers=[_power("p1")],
            servers=[_server("s1")],
            skills=[_skill("sk1")],
            steering_files=[_steering("st1")],
            pipeline_registries=[_pipeline("pl1")],
        )
        result = installer.install(manifest)

        assert result.success is False
        assert result.total_installed == 0
        assert len(result.failures) == 5

    def test_failure_continues_to_next_component(self) -> None:
        """After a failure, subsequent components of the same type still install."""
        rec = RecordingInstaller(fail_on={"s2"})
        installer = BundleInstaller(rec)

        manifest = _manifest(
            servers=[_server("s1"), _server("s2"), _server("s3")]
        )
        result = installer.install(manifest)

        assert result.installed_mcp_servers == 2
        assert len(result.failures) == 1
        installed_names = {c[1] for c in rec.calls if c[0] == "mcp_server"}
        assert installed_names == {"s1", "s3"}


# ---------------------------------------------------------------------------
# BundleInstaller — cyclic dependency handling
# ---------------------------------------------------------------------------


class TestCyclicDependencyHandling:
    """Cyclic dependencies cause all MCP servers to fail gracefully."""

    def test_cycle_fails_all_servers(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            servers=[
                _server("A", dependencies=["B"]),
                _server("B", dependencies=["A"]),
            ]
        )
        result = installer.install(manifest)

        assert result.installed_mcp_servers == 0
        assert len(result.failures) == 2
        for f in result.failures:
            assert f.component_type == "mcp_server"
            assert "Cyclic dependency" in f.reason or "cycle" in f.reason.lower()

    def test_cycle_does_not_block_other_types(self) -> None:
        """Powers, skills, etc. still install even when MCP servers have a cycle."""
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            powers=[_power("p1")],
            servers=[
                _server("A", dependencies=["B"]),
                _server("B", dependencies=["A"]),
            ],
            skills=[_skill("sk1")],
        )
        result = installer.install(manifest)

        assert result.installed_powers == 1
        assert result.installed_skills == 1
        assert result.installed_mcp_servers == 0


# ---------------------------------------------------------------------------
# BundleInstaller — installation order
# ---------------------------------------------------------------------------


class TestInstallationOrder:
    """Components are installed in the correct type order."""

    def test_powers_before_servers(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            powers=[_power("p1")],
            servers=[_server("s1")],
        )
        installer.install(manifest)

        types = [c[0] for c in rec.calls]
        assert types.index("power") < types.index("mcp_server")

    def test_servers_before_skills(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            servers=[_server("s1")],
            skills=[_skill("sk1")],
        )
        installer.install(manifest)

        types = [c[0] for c in rec.calls]
        assert types.index("mcp_server") < types.index("skill")

    def test_full_order(self) -> None:
        rec = RecordingInstaller()
        installer = BundleInstaller(rec)

        manifest = _manifest(
            powers=[_power("p1")],
            servers=[_server("s1")],
            skills=[_skill("sk1")],
            steering_files=[_steering("st1")],
            pipeline_registries=[_pipeline("pl1")],
        )
        installer.install(manifest)

        types = [c[0] for c in rec.calls]
        assert types == [
            "power",
            "mcp_server",
            "skill",
            "steering_file",
            "pipeline_registry",
        ]
