"""Bundle installer for the Kiro for Life Sciences bundle.

Orchestrates the installation of all components declared in a
:class:`BundleManifest`.  Uses the :class:`DependencyResolver` to determine
MCP server installation order and delegates actual per-component work to a
pluggable :class:`ComponentInstaller` protocol.

Key behaviours:
- Graceful failure handling: if a component fails, the error is recorded and
  installation continues with the remaining components.
- Summary reporting: counts of installed Powers, MCP Servers, Skills,
  Steering Files, and Pipeline Registries.
- Final failure summary listing every failed component with its name, type,
  and failure reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from kiro_life_sciences.installer.dependency_resolver import (
    CyclicDependencyError,
    DependencyResolver,
)
from kiro_life_sciences.models.manifest import BundleManifest


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InstallationFailure:
    """Records a single component that failed to install.

    Attributes:
        component_name: Human-readable name of the component.
        component_type: One of ``"power"``, ``"mcp_server"``, ``"skill"``,
            ``"steering_file"``, or ``"pipeline_registry"``.
        reason: A description of why the installation failed.
    """

    component_name: str
    component_type: str
    reason: str


@dataclass
class InstallationResult:
    """Aggregated outcome of a bundle installation.

    Attributes:
        installed_powers: Number of successfully installed Powers.
        installed_mcp_servers: Number of successfully installed MCP Servers.
        installed_skills: Number of successfully installed Skills.
        installed_steering_files: Number of successfully installed Steering Files.
        installed_pipeline_registries: Number of successfully installed Pipeline Registries.
        failures: List of components that failed to install.
    """

    installed_powers: int = 0
    installed_mcp_servers: int = 0
    installed_skills: int = 0
    installed_steering_files: int = 0
    installed_pipeline_registries: int = 0
    failures: list[InstallationFailure] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """``True`` when every component installed without failure."""
        return len(self.failures) == 0

    @property
    def total_installed(self) -> int:
        """Total number of successfully installed components across all types."""
        return (
            self.installed_powers
            + self.installed_mcp_servers
            + self.installed_skills
            + self.installed_steering_files
            + self.installed_pipeline_registries
        )


# ---------------------------------------------------------------------------
# Pluggable installer protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class ComponentInstaller(Protocol):
    """Strategy interface for installing individual components.

    Implementations handle the actual download-and-configure logic for each
    component type.  The :class:`BundleInstaller` calls these methods and
    catches any exceptions they raise, recording them as failures.
    """

    def install_power(self, name: str, version: str) -> None:
        """Install a Power component."""
        ...  # pragma: no cover

    def install_mcp_server(self, name: str, version: str) -> None:
        """Install an MCP Server component."""
        ...  # pragma: no cover

    def install_skill(self, name: str, filename: str) -> None:
        """Install a Skill component."""
        ...  # pragma: no cover

    def install_steering_file(self, name: str, filename: str) -> None:
        """Install a Steering File component."""
        ...  # pragma: no cover

    def install_pipeline_registry(self, name: str) -> None:
        """Install a Pipeline Registry component."""
        ...  # pragma: no cover


# ---------------------------------------------------------------------------
# Bundle installer
# ---------------------------------------------------------------------------


class BundleInstaller:
    """Installs all components declared in a :class:`BundleManifest`.

    Parameters:
        component_installer: A :class:`ComponentInstaller` implementation
            that handles the actual download/configure work for each
            component.
        dependency_resolver: An optional :class:`DependencyResolver`.  If
            ``None``, a default instance is created.
    """

    def __init__(
        self,
        component_installer: ComponentInstaller,
        dependency_resolver: DependencyResolver | None = None,
    ) -> None:
        self._installer = component_installer
        self._resolver = dependency_resolver or DependencyResolver()

    # -- public API ---------------------------------------------------------

    def install(self, manifest: BundleManifest) -> InstallationResult:
        """Install every component in *manifest* and return the result.

        Installation proceeds in the following order:

        1. Powers
        2. MCP Servers (in dependency-resolved order)
        3. Skills
        4. Steering Files
        5. Pipeline Registries

        If any individual component raises an exception during installation,
        the failure is recorded and installation continues with the next
        component.
        """
        result = InstallationResult()

        # 1. Powers
        self._install_powers(manifest, result)

        # 2. MCP Servers (dependency-resolved order)
        self._install_mcp_servers(manifest, result)

        # 3. Skills
        self._install_skills(manifest, result)

        # 4. Steering Files
        self._install_steering_files(manifest, result)

        # 5. Pipeline Registries
        self._install_pipeline_registries(manifest, result)

        return result

    # -- private helpers ----------------------------------------------------

    def _install_powers(
        self, manifest: BundleManifest, result: InstallationResult
    ) -> None:
        for power in manifest.components.powers:
            try:
                self._installer.install_power(power.name, power.version)
                result.installed_powers += 1
            except Exception as exc:  # noqa: BLE001
                result.failures.append(
                    InstallationFailure(
                        component_name=power.name,
                        component_type="power",
                        reason=str(exc),
                    )
                )

    def _install_mcp_servers(
        self, manifest: BundleManifest, result: InstallationResult
    ) -> None:
        # Build a name → server lookup for the manifest's MCP servers.
        server_map = {s.name: s for s in manifest.components.mcpServers}

        try:
            install_order = self._resolver.resolve(manifest)
        except CyclicDependencyError as exc:
            # If the dependency graph has a cycle we cannot determine a valid
            # order.  Record every MCP server as failed.
            for server in manifest.components.mcpServers:
                result.failures.append(
                    InstallationFailure(
                        component_name=server.name,
                        component_type="mcp_server",
                        reason=f"Dependency cycle detected: {exc}",
                    )
                )
            return

        for name in install_order:
            server = server_map.get(name)
            if server is None:
                # This name was injected by the resolver as an external
                # dependency not declared in the manifest — skip it.
                continue
            try:
                self._installer.install_mcp_server(server.name, server.version)
                result.installed_mcp_servers += 1
            except Exception as exc:  # noqa: BLE001
                result.failures.append(
                    InstallationFailure(
                        component_name=server.name,
                        component_type="mcp_server",
                        reason=str(exc),
                    )
                )

    def _install_skills(
        self, manifest: BundleManifest, result: InstallationResult
    ) -> None:
        for skill in manifest.components.skills:
            try:
                self._installer.install_skill(skill.name, skill.filename)
                result.installed_skills += 1
            except Exception as exc:  # noqa: BLE001
                result.failures.append(
                    InstallationFailure(
                        component_name=skill.name,
                        component_type="skill",
                        reason=str(exc),
                    )
                )

    def _install_steering_files(
        self, manifest: BundleManifest, result: InstallationResult
    ) -> None:
        for sf in manifest.components.steeringFiles:
            try:
                self._installer.install_steering_file(sf.name, sf.filename)
                result.installed_steering_files += 1
            except Exception as exc:  # noqa: BLE001
                result.failures.append(
                    InstallationFailure(
                        component_name=sf.name,
                        component_type="steering_file",
                        reason=str(exc),
                    )
                )

    def _install_pipeline_registries(
        self, manifest: BundleManifest, result: InstallationResult
    ) -> None:
        for reg in manifest.components.pipelineRegistries:
            try:
                self._installer.install_pipeline_registry(reg.name)
                result.installed_pipeline_registries += 1
            except Exception as exc:  # noqa: BLE001
                result.failures.append(
                    InstallationFailure(
                        component_name=reg.name,
                        component_type="pipeline_registry",
                        reason=str(exc),
                    )
                )
