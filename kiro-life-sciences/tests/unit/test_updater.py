"""Unit tests for the manifest diff and update logic."""

from __future__ import annotations

import pytest

from kiro_life_sciences.installer.updater import (
    ComponentChange,
    ManifestDiff,
    ManifestUpdater,
    _is_breaking,
    _parse_major,
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


def _manifest(
    *,
    powers: list[PowerReference] | None = None,
    mcp_servers: list[MCPServerReference] | None = None,
    skills: list[SkillReference] | None = None,
    steering_files: list[SteeringFileReference] | None = None,
    pipeline_registries: list[PipelineRegistryReference] | None = None,
    version: str = "1.0.0",
) -> BundleManifest:
    """Build a minimal :class:`BundleManifest` for testing."""
    return BundleManifest(
        name="test-bundle",
        version=version,
        description="test",
        components=BundleComponents(
            powers=powers or [],
            mcpServers=mcp_servers or [],
            skills=skills or [],
            steeringFiles=steering_files or [],
            pipelineRegistries=pipeline_registries or [],
        ),
        resourceCatalog=ResourceCatalogDefinition(entries=[]),
    )


def _power(name: str, version: str) -> PowerReference:
    return PowerReference(name=name, version=version, required=True, description="d")


def _server(name: str, version: str) -> MCPServerReference:
    return MCPServerReference(
        name=name,
        version=version,
        pypiPackage=name,
        description="d",
        domain="Genomics and Sequencing",
    )


def _skill(name: str, filename: str) -> SkillReference:
    return SkillReference(name=name, filename=filename, description="d", domain="Genomics")


def _steering(name: str, filename: str) -> SteeringFileReference:
    return SteeringFileReference(name=name, filename=filename, description="d", domain="Genomics")


def _registry(name: str) -> PipelineRegistryReference:
    return PipelineRegistryReference(
        name=name, workflowLanguage="WDL", source="test", description="d"
    )


# ---------------------------------------------------------------------------
# _parse_major / _is_breaking helpers
# ---------------------------------------------------------------------------


class TestParseMajor:
    def test_valid_semver(self) -> None:
        assert _parse_major("1.2.3") == 1
        assert _parse_major("0.0.1") == 0
        assert _parse_major("10.20.30") == 10

    def test_invalid_semver(self) -> None:
        assert _parse_major("not-a-version") is None
        assert _parse_major("1.2") is None
        assert _parse_major("") is None


class TestIsBreaking:
    def test_major_increase(self) -> None:
        assert _is_breaking("1.0.0", "2.0.0") is True
        assert _is_breaking("1.9.9", "3.0.0") is True

    def test_no_major_increase(self) -> None:
        assert _is_breaking("1.0.0", "1.1.0") is False
        assert _is_breaking("1.0.0", "1.0.1") is False

    def test_major_decrease(self) -> None:
        assert _is_breaking("2.0.0", "1.0.0") is False

    def test_same_version(self) -> None:
        assert _is_breaking("1.0.0", "1.0.0") is False

    def test_invalid_versions(self) -> None:
        assert _is_breaking("bad", "2.0.0") is False
        assert _is_breaking("1.0.0", "bad") is False


# ---------------------------------------------------------------------------
# ManifestDiff properties
# ---------------------------------------------------------------------------


class TestManifestDiffProperties:
    def test_empty_diff(self) -> None:
        diff = ManifestDiff(changes=[])
        assert diff.has_breaking_changes is False
        assert diff.added == []
        assert diff.removed == []
        assert diff.updated == []

    def test_has_breaking_changes(self) -> None:
        diff = ManifestDiff(
            changes=[
                ComponentChange("a", "power", "1.0.0", "2.0.0", True, "updated"),
            ]
        )
        assert diff.has_breaking_changes is True

    def test_no_breaking_changes(self) -> None:
        diff = ManifestDiff(
            changes=[
                ComponentChange("a", "power", "1.0.0", "1.1.0", False, "updated"),
            ]
        )
        assert diff.has_breaking_changes is False

    def test_added_removed_updated_filters(self) -> None:
        diff = ManifestDiff(
            changes=[
                ComponentChange("a", "power", None, "1.0.0", False, "added"),
                ComponentChange("b", "power", "1.0.0", None, False, "removed"),
                ComponentChange("c", "power", "1.0.0", "1.1.0", False, "updated"),
            ]
        )
        assert len(diff.added) == 1
        assert diff.added[0].name == "a"
        assert len(diff.removed) == 1
        assert diff.removed[0].name == "b"
        assert len(diff.updated) == 1
        assert diff.updated[0].name == "c"


# ---------------------------------------------------------------------------
# ManifestUpdater.diff — identical manifests
# ---------------------------------------------------------------------------


class TestDiffIdentical:
    def test_identical_empty_manifests(self) -> None:
        m = _manifest()
        diff = ManifestUpdater().diff(m, m)
        assert diff.changes == []

    def test_identical_populated_manifests(self) -> None:
        m = _manifest(
            powers=[_power("p1", "1.0.0")],
            mcp_servers=[_server("s1", "2.0.0")],
            skills=[_skill("sk1", "sk1.md")],
            steering_files=[_steering("sf1", "sf1.md")],
            pipeline_registries=[_registry("pr1")],
        )
        diff = ManifestUpdater().diff(m, m)
        assert diff.changes == []


# ---------------------------------------------------------------------------
# ManifestUpdater.diff — powers
# ---------------------------------------------------------------------------


class TestDiffPowers:
    def test_added_power(self) -> None:
        old = _manifest()
        new = _manifest(powers=[_power("p1", "1.0.0")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.name == "p1"
        assert c.component_type == "power"
        assert c.change_type == "added"
        assert c.old_version is None
        assert c.new_version == "1.0.0"
        assert c.is_breaking is False

    def test_removed_power(self) -> None:
        old = _manifest(powers=[_power("p1", "1.0.0")])
        new = _manifest()
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.change_type == "removed"
        assert c.old_version == "1.0.0"
        assert c.new_version is None

    def test_updated_power_minor(self) -> None:
        old = _manifest(powers=[_power("p1", "1.0.0")])
        new = _manifest(powers=[_power("p1", "1.1.0")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.change_type == "updated"
        assert c.is_breaking is False

    def test_updated_power_major_breaking(self) -> None:
        old = _manifest(powers=[_power("p1", "1.0.0")])
        new = _manifest(powers=[_power("p1", "2.0.0")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.change_type == "updated"
        assert c.is_breaking is True

    def test_unchanged_power_not_in_diff(self) -> None:
        old = _manifest(powers=[_power("p1", "1.0.0"), _power("p2", "1.0.0")])
        new = _manifest(powers=[_power("p1", "1.0.0"), _power("p2", "1.1.0")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].name == "p2"


# ---------------------------------------------------------------------------
# ManifestUpdater.diff — MCP servers
# ---------------------------------------------------------------------------


class TestDiffMCPServers:
    def test_added_server(self) -> None:
        old = _manifest()
        new = _manifest(mcp_servers=[_server("s1", "1.0.0")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].component_type == "mcp_server"
        assert diff.changes[0].change_type == "added"

    def test_removed_server(self) -> None:
        old = _manifest(mcp_servers=[_server("s1", "1.0.0")])
        new = _manifest()
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == "removed"

    def test_updated_server_breaking(self) -> None:
        old = _manifest(mcp_servers=[_server("s1", "1.0.0")])
        new = _manifest(mcp_servers=[_server("s1", "3.0.0")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.change_type == "updated"
        assert c.is_breaking is True
        assert c.old_version == "1.0.0"
        assert c.new_version == "3.0.0"


# ---------------------------------------------------------------------------
# ManifestUpdater.diff — skills (filename-based)
# ---------------------------------------------------------------------------


class TestDiffSkills:
    def test_added_skill(self) -> None:
        old = _manifest()
        new = _manifest(skills=[_skill("sk1", "sk1.md")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.component_type == "skill"
        assert c.change_type == "added"
        assert c.old_version is None
        assert c.new_version == "sk1.md"

    def test_removed_skill(self) -> None:
        old = _manifest(skills=[_skill("sk1", "sk1.md")])
        new = _manifest()
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == "removed"

    def test_updated_skill_filename(self) -> None:
        old = _manifest(skills=[_skill("sk1", "sk1_v1.md")])
        new = _manifest(skills=[_skill("sk1", "sk1_v2.md")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.change_type == "updated"
        assert c.is_breaking is False  # skills are never breaking

    def test_unchanged_skill(self) -> None:
        old = _manifest(skills=[_skill("sk1", "sk1.md")])
        new = _manifest(skills=[_skill("sk1", "sk1.md")])
        diff = ManifestUpdater().diff(old, new)
        assert diff.changes == []


# ---------------------------------------------------------------------------
# ManifestUpdater.diff — steering files (filename-based)
# ---------------------------------------------------------------------------


class TestDiffSteeringFiles:
    def test_added_steering_file(self) -> None:
        old = _manifest()
        new = _manifest(steering_files=[_steering("sf1", "sf1.md")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].component_type == "steering_file"
        assert diff.changes[0].change_type == "added"

    def test_removed_steering_file(self) -> None:
        old = _manifest(steering_files=[_steering("sf1", "sf1.md")])
        new = _manifest()
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == "removed"

    def test_updated_steering_file(self) -> None:
        old = _manifest(steering_files=[_steering("sf1", "old.md")])
        new = _manifest(steering_files=[_steering("sf1", "new.md")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.change_type == "updated"
        assert c.is_breaking is False


# ---------------------------------------------------------------------------
# ManifestUpdater.diff — pipeline registries (name-only)
# ---------------------------------------------------------------------------


class TestDiffPipelineRegistries:
    def test_added_registry(self) -> None:
        old = _manifest()
        new = _manifest(pipeline_registries=[_registry("pr1")])
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        c = diff.changes[0]
        assert c.component_type == "pipeline_registry"
        assert c.change_type == "added"
        assert c.old_version is None
        assert c.new_version is None

    def test_removed_registry(self) -> None:
        old = _manifest(pipeline_registries=[_registry("pr1")])
        new = _manifest()
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == "removed"

    def test_unchanged_registry(self) -> None:
        old = _manifest(pipeline_registries=[_registry("pr1")])
        new = _manifest(pipeline_registries=[_registry("pr1")])
        diff = ManifestUpdater().diff(old, new)
        assert diff.changes == []


# ---------------------------------------------------------------------------
# ManifestUpdater.diff — mixed changes across component types
# ---------------------------------------------------------------------------


class TestDiffMixed:
    def test_multiple_component_types_changed(self) -> None:
        old = _manifest(
            powers=[_power("p1", "1.0.0")],
            mcp_servers=[_server("s1", "1.0.0"), _server("s2", "1.0.0")],
            skills=[_skill("sk1", "sk1.md")],
            steering_files=[_steering("sf1", "sf1.md")],
            pipeline_registries=[_registry("pr1")],
        )
        new = _manifest(
            powers=[_power("p1", "2.0.0")],  # updated (breaking)
            mcp_servers=[_server("s1", "1.0.0"), _server("s3", "1.0.0")],  # s2 removed, s3 added
            skills=[_skill("sk1", "sk1.md"), _skill("sk2", "sk2.md")],  # sk2 added
            steering_files=[],  # sf1 removed
            pipeline_registries=[_registry("pr1"), _registry("pr2")],  # pr2 added
        )
        diff = ManifestUpdater().diff(old, new)

        assert diff.has_breaking_changes is True

        names_by_type = {}
        for c in diff.changes:
            names_by_type.setdefault(c.change_type, []).append(c.name)

        assert "p1" in names_by_type["updated"]
        assert "s2" in names_by_type["removed"]
        assert "s3" in names_by_type["added"]
        assert "sk2" in names_by_type["added"]
        assert "sf1" in names_by_type["removed"]
        assert "pr2" in names_by_type["added"]

    def test_diff_only_contains_changed_components(self) -> None:
        """Unchanged components must NOT appear in the diff."""
        old = _manifest(
            powers=[_power("p1", "1.0.0"), _power("p2", "1.0.0")],
            mcp_servers=[_server("s1", "1.0.0")],
        )
        new = _manifest(
            powers=[_power("p1", "1.0.0"), _power("p2", "1.1.0")],
            mcp_servers=[_server("s1", "1.0.0")],
        )
        diff = ManifestUpdater().diff(old, new)
        assert len(diff.changes) == 1
        assert diff.changes[0].name == "p2"
