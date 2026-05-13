"""Dependency resolver for the Kiro for Life Sciences bundle.

Provides topological sorting of component dependencies, version conflict
detection, and cycle detection for the bundle manifest's MCP servers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kiro_life_sciences.models.manifest import BundleManifest


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------


class CyclicDependencyError(Exception):
    """Raised when the dependency graph contains a cycle.

    Attributes:
        cycle: The list of component names forming the cycle.  The first and
            last elements are the same node, e.g. ``["A", "B", "C", "A"]``.
    """

    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        path_str = " -> ".join(cycle)
        super().__init__(f"Cyclic dependency detected: {path_str}")


@dataclass(frozen=True)
class VersionConflict:
    """Describes a version conflict for a single dependency.

    Attributes:
        dependency: The name of the dependency that has conflicting versions.
        required_by: Mapping of *requester name* → *requested version*.
    """

    dependency: str
    required_by: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------


class DependencyResolver:
    """Resolves installation order and detects conflicts for bundle components.

    The resolver operates on the ``mcpServers`` list inside a
    :class:`BundleManifest`.  Each server may declare ``dependencies`` — a
    list of other MCP server names that must be installed first.
    """

    # -- public API ---------------------------------------------------------

    def resolve(self, manifest: BundleManifest) -> list[str]:
        """Return MCP server names in a valid installation order.

        The returned list satisfies the constraint that every server's
        dependencies appear *before* it in the list, and every declared
        server appears exactly once.

        Raises:
            CyclicDependencyError: If the dependency graph contains a cycle.
        """
        servers = {s.name: s.dependencies for s in manifest.components.mcpServers}
        return self._topological_sort(servers)

    def detect_conflicts(self, manifest: BundleManifest) -> list[VersionConflict]:
        """Return version conflicts between MCP servers in the manifest.

        A conflict exists when two or more servers list the same dependency
        name in their ``dependencies`` field but the manifest contains only
        one version of that dependency.  More precisely, if two servers
        *themselves* share the same ``name`` but differ in ``version``, that
        is a conflict.

        In this model each MCP server is uniquely identified by ``name``.
        A version conflict arises when the manifest contains duplicate
        server names with different versions, or when multiple servers
        depend on the same server name but expect different versions.

        Because the manifest's ``dependencies`` field only stores *names*
        (not version constraints), the practical conflict scenario is when
        the manifest itself lists the same server name more than once with
        different versions.
        """
        # Collect all (name, version) pairs from the manifest.
        server_versions: dict[str, list[str]] = {}
        for server in manifest.components.mcpServers:
            server_versions.setdefault(server.name, []).append(server.version)

        conflicts: list[VersionConflict] = []

        for name, versions in sorted(server_versions.items()):
            unique_versions = set(versions)
            if len(unique_versions) > 1:
                # Build required_by with distinguishable keys when the same
                # name appears multiple times.
                required_by: dict[str, str] = {}
                for idx, ver in enumerate(versions):
                    key = name if idx == 0 else f"{name} (entry {idx + 1})"
                    required_by[key] = ver
                conflicts.append(
                    VersionConflict(dependency=name, required_by=required_by)
                )

        return conflicts

    # -- internals ----------------------------------------------------------

    @staticmethod
    def _topological_sort(graph: dict[str, list[str]]) -> list[str]:
        """Kahn's algorithm with cycle detection.

        Parameters:
            graph: Mapping of node name → list of dependency names.

        Returns:
            A list of node names in topological (install) order.

        Raises:
            CyclicDependencyError: If the graph contains a cycle.
        """
        # Build adjacency list and in-degree map.
        # An edge from A → B means "A depends on B", so B must come first.
        # We invert this: adj[B] contains A (B is depended upon by A).
        adj: dict[str, list[str]] = {node: [] for node in graph}
        in_degree: dict[str, int] = {node: 0 for node in graph}

        for node, deps in graph.items():
            for dep in deps:
                # If the dependency isn't declared as a top-level server,
                # add it to the graph as a node with no dependencies.
                if dep not in adj:
                    adj[dep] = []
                    in_degree[dep] = 0
                adj[dep].append(node)
                in_degree[node] += 1

        # Seed the queue with nodes that have no dependencies.
        queue: list[str] = sorted(
            [n for n, d in in_degree.items() if d == 0]
        )
        order: list[str] = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbour in sorted(adj[node]):
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)
            # Keep queue sorted for deterministic output.
            queue.sort()

        if len(order) != len(in_degree):
            # There is a cycle — find it for the error message.
            remaining = {n for n, d in in_degree.items() if n not in set(order)}
            cycle = DependencyResolver._find_cycle(graph, remaining)
            raise CyclicDependencyError(cycle)

        return order

    @staticmethod
    def _find_cycle(
        graph: dict[str, list[str]], candidates: set[str]
    ) -> list[str]:
        """Find and return one cycle path within *candidates*.

        Uses iterative DFS with explicit stack to avoid recursion limits.
        Returns a list like ``["A", "B", "C", "A"]``.
        """
        visited: set[str] = set()

        for start in sorted(candidates):
            if start in visited:
                continue

            # Stack entries: (node, iterator over its dependencies)
            path: list[str] = []
            path_set: set[str] = set()
            stack: list[tuple[str, int]] = [(start, 0)]

            while stack:
                node, idx = stack[-1]

                if node not in path_set:
                    path.append(node)
                    path_set.add(node)

                deps = [d for d in graph.get(node, []) if d in candidates]

                if idx < len(deps):
                    stack[-1] = (node, idx + 1)
                    dep = deps[idx]
                    if dep in path_set:
                        # Found a cycle.
                        cycle_start = path.index(dep)
                        return path[cycle_start:] + [dep]
                    if dep not in visited:
                        stack.append((dep, 0))
                else:
                    stack.pop()
                    path.pop()
                    path_set.discard(node)
                    visited.add(node)

        # Fallback — shouldn't happen if candidates truly contain a cycle.
        return list(candidates)  # pragma: no cover
