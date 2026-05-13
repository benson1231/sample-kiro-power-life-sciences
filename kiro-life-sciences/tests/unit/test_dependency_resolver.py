"""Unit tests for the dependency resolver."""

from __future__ import annotations

import pytest

from kiro_life_sciences.installer.dependency_resolver import (
    CyclicDependencyError,
    DependencyResolver,
    VersionConflict,
)
from kiro_life_sciences.models.manifest import (
    BundleComponents,
    BundleManifest,
    MCPServerReference,
    ResourceCatalogDefinition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _server(
    name: str,
    version: str = "1.0.0",
    dependencies: list[str] | None = None,
) -> MCPServerReference:
    """Create a minimal MCPServerReference for testing."""
    return MCPServerReference(
        name=name,
        version=version,
        pypiPackage=name,
        description=f"Test server {name}",
        domain="Test",
        dependencies=dependencies or [],
    )


def _manifest(servers: list[MCPServerReference]) -> BundleManifest:
    """Create a minimal BundleManifest wrapping the given servers."""
    return BundleManifest(
        name="test-bundle",
        version="1.0.0",
        description="Test bundle",
        components=BundleComponents(mcpServers=servers),
        resourceCatalog=ResourceCatalogDefinition(),
    )


# ---------------------------------------------------------------------------
# DependencyResolver.resolve — topological sort
# ---------------------------------------------------------------------------


class TestResolveOrder:
    """Tests for DependencyResolver.resolve()."""

    def test_empty_manifest(self) -> None:
        resolver = DependencyResolver()
        result = resolver.resolve(_manifest([]))
        assert result == []

    def test_single_server_no_deps(self) -> None:
        resolver = DependencyResolver()
        result = resolver.resolve(_manifest([_server("alpha")]))
        assert result == ["alpha"]

    def test_multiple_servers_no_deps(self) -> None:
        """Servers with no dependencies should all appear (sorted deterministically)."""
        resolver = DependencyResolver()
        servers = [_server("charlie"), _server("alpha"), _server("bravo")]
        result = resolver.resolve(_manifest(servers))
        assert set(result) == {"alpha", "bravo", "charlie"}
        assert len(result) == 3

    def test_linear_chain(self) -> None:
        """A -> B -> C  ⇒  install order is C, B, A."""
        resolver = DependencyResolver()
        servers = [
            _server("A", dependencies=["B"]),
            _server("B", dependencies=["C"]),
            _server("C"),
        ]
        result = resolver.resolve(_manifest(servers))
        assert result.index("C") < result.index("B") < result.index("A")

    def test_diamond_dependency(self) -> None:
        """Diamond: A->B, A->C, B->D, C->D  ⇒  D before B and C, both before A."""
        resolver = DependencyResolver()
        servers = [
            _server("A", dependencies=["B", "C"]),
            _server("B", dependencies=["D"]),
            _server("C", dependencies=["D"]),
            _server("D"),
        ]
        result = resolver.resolve(_manifest(servers))
        assert result.index("D") < result.index("B")
        assert result.index("D") < result.index("C")
        assert result.index("B") < result.index("A")
        assert result.index("C") < result.index("A")

    def test_all_components_appear_exactly_once(self) -> None:
        resolver = DependencyResolver()
        servers = [
            _server("X", dependencies=["Y"]),
            _server("Y", dependencies=["Z"]),
            _server("Z"),
        ]
        result = resolver.resolve(_manifest(servers))
        assert len(result) == len(set(result))
        assert set(result) == {"X", "Y", "Z"}

    def test_dependency_on_undeclared_server(self) -> None:
        """If a server depends on a name not in the manifest, it still appears."""
        resolver = DependencyResolver()
        servers = [_server("A", dependencies=["external"])]
        result = resolver.resolve(_manifest(servers))
        # "external" is added as a node with no deps
        assert "external" in result
        assert result.index("external") < result.index("A")


# ---------------------------------------------------------------------------
# DependencyResolver.resolve — cycle detection
# ---------------------------------------------------------------------------


class TestCycleDetection:
    """Tests for cycle detection in resolve()."""

    def test_self_cycle(self) -> None:
        resolver = DependencyResolver()
        servers = [_server("A", dependencies=["A"])]
        with pytest.raises(CyclicDependencyError) as exc_info:
            resolver.resolve(_manifest(servers))
        assert "A" in exc_info.value.cycle

    def test_two_node_cycle(self) -> None:
        resolver = DependencyResolver()
        servers = [
            _server("A", dependencies=["B"]),
            _server("B", dependencies=["A"]),
        ]
        with pytest.raises(CyclicDependencyError) as exc_info:
            resolver.resolve(_manifest(servers))
        cycle = exc_info.value.cycle
        assert cycle[0] == cycle[-1]  # cycle is closed
        assert len(cycle) >= 3  # at least A -> B -> A

    def test_three_node_cycle(self) -> None:
        resolver = DependencyResolver()
        servers = [
            _server("A", dependencies=["B"]),
            _server("B", dependencies=["C"]),
            _server("C", dependencies=["A"]),
        ]
        with pytest.raises(CyclicDependencyError) as exc_info:
            resolver.resolve(_manifest(servers))
        cycle = exc_info.value.cycle
        assert cycle[0] == cycle[-1]
        assert set(cycle[:-1]) == {"A", "B", "C"}

    def test_cycle_error_message_contains_path(self) -> None:
        resolver = DependencyResolver()
        servers = [
            _server("X", dependencies=["Y"]),
            _server("Y", dependencies=["X"]),
        ]
        with pytest.raises(CyclicDependencyError, match="Cyclic dependency detected"):
            resolver.resolve(_manifest(servers))

    def test_cycle_with_non_cyclic_nodes(self) -> None:
        """Graph has both a cycle and non-cyclic nodes."""
        resolver = DependencyResolver()
        servers = [
            _server("ok1"),
            _server("ok2", dependencies=["ok1"]),
            _server("cyc1", dependencies=["cyc2"]),
            _server("cyc2", dependencies=["cyc1"]),
        ]
        with pytest.raises(CyclicDependencyError):
            resolver.resolve(_manifest(servers))


# ---------------------------------------------------------------------------
# DependencyResolver.detect_conflicts
# ---------------------------------------------------------------------------


class TestDetectConflicts:
    """Tests for version conflict detection."""

    def test_no_conflicts(self) -> None:
        resolver = DependencyResolver()
        servers = [_server("A", version="1.0.0"), _server("B", version="2.0.0")]
        conflicts = resolver.detect_conflicts(_manifest(servers))
        assert conflicts == []

    def test_duplicate_name_different_versions(self) -> None:
        resolver = DependencyResolver()
        servers = [
            _server("A", version="1.0.0"),
            _server("A", version="2.0.0"),
        ]
        conflicts = resolver.detect_conflicts(_manifest(servers))
        assert len(conflicts) == 1
        assert conflicts[0].dependency == "A"
        versions = set(conflicts[0].required_by.values())
        assert versions == {"1.0.0", "2.0.0"}

    def test_duplicate_name_same_version_no_conflict(self) -> None:
        resolver = DependencyResolver()
        servers = [
            _server("A", version="1.0.0"),
            _server("A", version="1.0.0"),
        ]
        conflicts = resolver.detect_conflicts(_manifest(servers))
        assert conflicts == []

    def test_multiple_conflicts(self) -> None:
        resolver = DependencyResolver()
        servers = [
            _server("A", version="1.0.0"),
            _server("A", version="2.0.0"),
            _server("B", version="1.0.0"),
            _server("B", version="3.0.0"),
            _server("C", version="1.0.0"),
        ]
        conflicts = resolver.detect_conflicts(_manifest(servers))
        conflict_names = {c.dependency for c in conflicts}
        assert conflict_names == {"A", "B"}


# ---------------------------------------------------------------------------
# VersionConflict data class
# ---------------------------------------------------------------------------


class TestVersionConflict:
    """Tests for the VersionConflict data class."""

    def test_fields(self) -> None:
        vc = VersionConflict(
            dependency="lib",
            required_by={"server-a": "1.0.0", "server-b": "2.0.0"},
        )
        assert vc.dependency == "lib"
        assert vc.required_by == {"server-a": "1.0.0", "server-b": "2.0.0"}

    def test_default_required_by(self) -> None:
        vc = VersionConflict(dependency="lib")
        assert vc.required_by == {}


# ---------------------------------------------------------------------------
# CyclicDependencyError
# ---------------------------------------------------------------------------


class TestCyclicDependencyError:
    """Tests for the CyclicDependencyError exception."""

    def test_cycle_attribute(self) -> None:
        err = CyclicDependencyError(["A", "B", "A"])
        assert err.cycle == ["A", "B", "A"]

    def test_str_representation(self) -> None:
        err = CyclicDependencyError(["A", "B", "C", "A"])
        assert str(err) == "Cyclic dependency detected: A -> B -> C -> A"
