"""Onboarding dashboard renderer.

Generates a structured dashboard from the bundle manifest, installed MCP
server state, and configured credential state.  The dashboard groups
resources by category, computes per-resource status, and renders a
markdown summary suitable for display in Kiro.

Design document reference: *Components and Interfaces §3 — Onboarding
Dashboard*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from kiro_life_sciences.models.catalog import ResourceCategory

if TYPE_CHECKING:
    from kiro_life_sciences.models.manifest import BundleManifest


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class DashboardResource:
    """A single resource shown on the dashboard."""

    name: str
    description: str
    status: str  # "ready" | "needs_setup" | "needs_credentials"
    mcpServer: str
    mcpServerInstalled: bool
    credentialInstructions: str | None = None
    quickAccessCommand: str | None = None


@dataclass
class DashboardCategory:
    """A group of resources under a single category."""

    name: ResourceCategory
    resourceCount: int
    resources: list[DashboardResource] = field(default_factory=list)


@dataclass
class DashboardSummary:
    """Aggregate counts displayed in the summary header."""

    totalDatabases: int = 0
    totalMCPServers: int = 0
    totalSkills: int = 0
    totalPipelines: int = 0
    totalSteeringFiles: int = 0
    installedMCPServers: int = 0
    configuredCredentials: int = 0


@dataclass
class DashboardData:
    """Complete dashboard payload."""

    summary: DashboardSummary = field(default_factory=DashboardSummary)
    categories: list[DashboardCategory] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

_STATUS_READY = "ready"
_STATUS_NEEDS_CREDENTIALS = "needs_credentials"
_STATUS_NEEDS_SETUP = "needs_setup"


def compute_resource_status(
    server_installed: bool,
    required_credential_env_vars: list[str],
    configured_credentials: set[str],
) -> str:
    """Compute the status for a single resource.

    Rules (design doc §3):
    - ``ready``: MCP server installed AND all required credentials configured.
    - ``needs_credentials``: MCP server installed BUT at least one required
      credential is missing.
    - ``needs_setup``: MCP server is NOT installed.
    """
    if not server_installed:
        return _STATUS_NEEDS_SETUP

    if required_credential_env_vars:
        missing = [v for v in required_credential_env_vars if v not in configured_credentials]
        if missing:
            return _STATUS_NEEDS_CREDENTIALS

    return _STATUS_READY


# ---------------------------------------------------------------------------
# Markdown rendering helpers
# ---------------------------------------------------------------------------

_STATUS_ICONS: dict[str, str] = {
    _STATUS_READY: "✅ Ready",
    _STATUS_NEEDS_CREDENTIALS: "⚠️ Needs Credentials",
    _STATUS_NEEDS_SETUP: "📦 Needs Setup",
}


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


class DashboardRenderer:
    """Generates :class:`DashboardData` and renders it as markdown.

    Parameters
    ----------
    manifest:
        The parsed ``BundleManifest``.
    installed_servers:
        Set of MCP server names that are currently configured in ``mcp.json``.
    configured_credentials:
        Set of environment variable names for which credentials have been
        configured (e.g. ``{"NCBI_API_KEY", "OMIM_API_KEY"}``).
    """

    def __init__(
        self,
        manifest: BundleManifest,
        installed_servers: set[str],
        configured_credentials: set[str],
    ) -> None:
        self._manifest = manifest
        self._installed_servers = installed_servers
        self._configured_credentials = configured_credentials

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> DashboardData:
        """Build the full :class:`DashboardData` from the manifest."""
        summary = self._build_summary()
        categories = self._build_categories()
        return DashboardData(summary=summary, categories=categories)

    def render_markdown(self) -> str:
        """Return a markdown string representing the dashboard."""
        data = self.generate()
        return self._render(data)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def _build_summary(self) -> DashboardSummary:
        components = self._manifest.components

        total_databases = sum(
            len(server.databases) for server in components.mcpServers
        )
        total_mcp_servers = len(components.mcpServers)
        total_skills = len(components.skills)
        total_pipelines = len(components.pipelineRegistries)
        total_steering_files = len(components.steeringFiles)

        installed_mcp_servers = sum(
            1 for s in components.mcpServers if s.name in self._installed_servers
        )

        # Count configured credentials across all servers
        configured_count = 0
        for server in components.mcpServers:
            for cred in server.credentials:
                if cred.envVar in self._configured_credentials:
                    configured_count += 1

        return DashboardSummary(
            totalDatabases=total_databases,
            totalMCPServers=total_mcp_servers,
            totalSkills=total_skills,
            totalPipelines=total_pipelines,
            totalSteeringFiles=total_steering_files,
            installedMCPServers=installed_mcp_servers,
            configuredCredentials=configured_count,
        )

    # ------------------------------------------------------------------
    # Categories & resources
    # ------------------------------------------------------------------

    def _build_categories(self) -> list[DashboardCategory]:
        """Group resources by domain/category from the manifest MCP servers."""
        category_map: dict[str, list[DashboardResource]] = {}

        for server in self._manifest.components.mcpServers:
            server_installed = server.name in self._installed_servers

            # Collect required credential env vars for this server
            required_cred_vars = [
                c.envVar for c in server.credentials if c.required
            ]

            for db in server.databases:
                # Determine which credentials are relevant to this database
                db_cred_vars = required_cred_vars

                status = compute_resource_status(
                    server_installed=server_installed,
                    required_credential_env_vars=db_cred_vars,
                    configured_credentials=self._configured_credentials,
                )

                # Build credential instructions if needed
                cred_instructions = self._credential_instructions_for_server(server) if status == _STATUS_NEEDS_CREDENTIALS else None

                quick_cmd = f"uvx {server.pypiPackage}" if server_installed else None

                resource = DashboardResource(
                    name=db.name,
                    description=db.description,
                    status=status,
                    mcpServer=server.name,
                    mcpServerInstalled=server_installed,
                    credentialInstructions=cred_instructions,
                    quickAccessCommand=quick_cmd,
                )

                category_map.setdefault(server.domain, []).append(resource)

        # Also add skills as resources
        for skill in self._manifest.components.skills:
            resource = DashboardResource(
                name=skill.name,
                description=skill.description,
                status=_STATUS_READY,
                mcpServer="",
                mcpServerInstalled=True,
                credentialInstructions=None,
                quickAccessCommand=None,
            )
            category_map.setdefault(skill.domain, []).append(resource)

        # Also add steering files as resources
        for sf in self._manifest.components.steeringFiles:
            resource = DashboardResource(
                name=sf.name,
                description=sf.description,
                status=_STATUS_READY,
                mcpServer="",
                mcpServerInstalled=True,
                credentialInstructions=None,
                quickAccessCommand=None,
            )
            category_map.setdefault(sf.domain, []).append(resource)

        # Convert to DashboardCategory list, sorted by category name
        categories: list[DashboardCategory] = []
        for cat_name in sorted(category_map.keys()):
            resources = category_map[cat_name]
            # Try to map to ResourceCategory enum; fall back to raw string
            try:
                rc = ResourceCategory(cat_name)
            except ValueError:
                rc = cat_name  # type: ignore[assignment]

            categories.append(
                DashboardCategory(
                    name=rc,
                    resourceCount=len(resources),
                    resources=resources,
                )
            )

        return categories

    # ------------------------------------------------------------------
    # Credential instructions
    # ------------------------------------------------------------------

    @staticmethod
    def _credential_instructions_for_server(server) -> str:
        """Build a human-readable credential setup instruction string."""
        lines: list[str] = []
        for cred in server.credentials:
            if cred.required:
                lines.append(
                    f"- {cred.name} ({cred.type}): {cred.description} — "
                    f"obtain at {cred.obtainUrl}, set env var {cred.envVar}"
                )
        return "\n".join(lines) if lines else ""

    # ------------------------------------------------------------------
    # Markdown rendering
    # ------------------------------------------------------------------

    @staticmethod
    def _render(data: DashboardData) -> str:
        """Render :class:`DashboardData` as a markdown string."""
        lines: list[str] = []

        # --- Summary header ---
        s = data.summary
        lines.append("# 🧬 Kiro for Life Sciences — Onboarding Dashboard")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"| Metric | Count |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Databases | {s.totalDatabases} |")
        lines.append(f"| MCP Servers | {s.totalMCPServers} |")
        lines.append(f"| Skills | {s.totalSkills} |")
        lines.append(f"| Pipelines | {s.totalPipelines} |")
        lines.append(f"| Steering Files | {s.totalSteeringFiles} |")
        lines.append(f"| Installed MCP Servers | {s.installedMCPServers} |")
        lines.append(f"| Configured Credentials | {s.configuredCredentials} |")
        lines.append("")

        # --- Categories ---
        for cat in data.categories:
            lines.append(f"## {cat.name} ({cat.resourceCount} resources)")
            lines.append("")

            for res in cat.resources:
                status_label = _STATUS_ICONS.get(res.status, res.status)
                lines.append(f"### {res.name}")
                lines.append("")
                lines.append(f"- **Status:** {status_label}")
                lines.append(f"- **Description:** {res.description}")

                if res.mcpServer:
                    lines.append(f"- **MCP Server:** {res.mcpServer}")

                if res.quickAccessCommand:
                    lines.append(f"- **Quick Access:** `{res.quickAccessCommand}`")

                if res.credentialInstructions:
                    lines.append(f"- **Credential Setup:**")
                    lines.append(f"  {res.credentialInstructions}")

                lines.append("")

        return "\n".join(lines)
