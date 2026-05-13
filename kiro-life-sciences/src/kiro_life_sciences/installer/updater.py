"""Manifest diff and selective update logic.

Compares two :class:`BundleManifest` versions and produces a
:class:`ManifestDiff` describing exactly which components changed.
Any component whose major version increased is flagged as a breaking change.

Component types compared:

* **Powers** and **MCP Servers** — versioned, compared by ``(name, version)``.
* **Skills** and **Steering Files** — unversioned, compared by ``(name, filename)``.
* **Pipeline Registries** — unversioned, compared by ``name`` only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from kiro_life_sciences.models.manifest import BundleManifest


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComponentChange:
    """A single component that differs between two manifest versions.

    Attributes:
        name: Human-readable component name.
        component_type: One of ``"power"``, ``"mcp_server"``, ``"skill"``,
            ``"steering_file"``, or ``"pipeline_registry"``.
        old_version: Version string in the old manifest, or ``None`` if newly added.
        new_version: Version string in the new manifest, or ``None`` if removed.
        is_breaking: ``True`` when the major version increased.
        change_type: One of ``"added"``, ``"removed"``, or ``"updated"``.
    """

    name: str
    component_type: str
    old_version: str | None
    new_version: str | None
    is_breaking: bool
    change_type: str  # "added" | "removed" | "updated"


@dataclass
class ManifestDiff:
    """The complete set of changes between two manifest versions.

    Attributes:
        changes: All detected component changes.
    """

    changes: list[ComponentChange] = field(default_factory=list)

    # -- convenience properties ---------------------------------------------

    @property
    def has_breaking_changes(self) -> bool:
        """``True`` if any change is flagged as breaking."""
        return any(c.is_breaking for c in self.changes)

    @property
    def added(self) -> list[ComponentChange]:
        """Components present in the new manifest but absent from the old."""
        return [c for c in self.changes if c.change_type == "added"]

    @property
    def removed(self) -> list[ComponentChange]:
        """Components present in the old manifest but absent from the new."""
        return [c for c in self.changes if c.change_type == "removed"]

    @property
    def updated(self) -> list[ComponentChange]:
        """Components present in both manifests but with a different version."""
        return [c for c in self.changes if c.change_type == "updated"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _parse_major(version: str) -> int | None:
    """Return the major component of a semver string, or ``None``."""
    m = _SEMVER_RE.match(version)
    if m is None:
        return None
    return int(m.group(1))


def _is_breaking(old_version: str, new_version: str) -> bool:
    """Return ``True`` when *new_version* has a higher major than *old_version*."""
    old_major = _parse_major(old_version)
    new_major = _parse_major(new_version)
    if old_major is None or new_major is None:
        return False
    return new_major > old_major


# ---------------------------------------------------------------------------
# Diff helpers for each component type
# ---------------------------------------------------------------------------


def _diff_versioned(
    old_items: dict[str, str],
    new_items: dict[str, str],
    component_type: str,
) -> list[ComponentChange]:
    """Diff two ``{name: version}`` mappings (powers, mcp_servers)."""
    changes: list[ComponentChange] = []
    all_names = set(old_items) | set(new_items)
    for name in sorted(all_names):
        old_ver = old_items.get(name)
        new_ver = new_items.get(name)
        if old_ver is None and new_ver is not None:
            changes.append(
                ComponentChange(
                    name=name,
                    component_type=component_type,
                    old_version=None,
                    new_version=new_ver,
                    is_breaking=False,
                    change_type="added",
                )
            )
        elif old_ver is not None and new_ver is None:
            changes.append(
                ComponentChange(
                    name=name,
                    component_type=component_type,
                    old_version=old_ver,
                    new_version=None,
                    is_breaking=False,
                    change_type="removed",
                )
            )
        elif old_ver != new_ver:
            # Both are not None here (checked above).
            assert old_ver is not None and new_ver is not None
            changes.append(
                ComponentChange(
                    name=name,
                    component_type=component_type,
                    old_version=old_ver,
                    new_version=new_ver,
                    is_breaking=_is_breaking(old_ver, new_ver),
                    change_type="updated",
                )
            )
    return changes


def _diff_filename_based(
    old_items: dict[str, str],
    new_items: dict[str, str],
    component_type: str,
) -> list[ComponentChange]:
    """Diff two ``{name: filename}`` mappings (skills, steering_files).

    Since these components are unversioned, the *filename* acts as the
    version proxy.  If the filename changes for the same name, it is an
    update.
    """
    changes: list[ComponentChange] = []
    all_names = set(old_items) | set(new_items)
    for name in sorted(all_names):
        old_fn = old_items.get(name)
        new_fn = new_items.get(name)
        if old_fn is None and new_fn is not None:
            changes.append(
                ComponentChange(
                    name=name,
                    component_type=component_type,
                    old_version=None,
                    new_version=new_fn,
                    is_breaking=False,
                    change_type="added",
                )
            )
        elif old_fn is not None and new_fn is None:
            changes.append(
                ComponentChange(
                    name=name,
                    component_type=component_type,
                    old_version=old_fn,
                    new_version=None,
                    is_breaking=False,
                    change_type="removed",
                )
            )
        elif old_fn != new_fn:
            assert old_fn is not None and new_fn is not None
            changes.append(
                ComponentChange(
                    name=name,
                    component_type=component_type,
                    old_version=old_fn,
                    new_version=new_fn,
                    is_breaking=False,
                    change_type="updated",
                )
            )
    return changes


def _diff_name_only(
    old_names: set[str],
    new_names: set[str],
    component_type: str,
) -> list[ComponentChange]:
    """Diff two sets of names (pipeline_registries).

    Pipeline registries are unversioned and have no filename — only the
    name is compared.
    """
    changes: list[ComponentChange] = []
    for name in sorted(old_names - new_names):
        changes.append(
            ComponentChange(
                name=name,
                component_type=component_type,
                old_version=None,
                new_version=None,
                is_breaking=False,
                change_type="removed",
            )
        )
    for name in sorted(new_names - old_names):
        changes.append(
            ComponentChange(
                name=name,
                component_type=component_type,
                old_version=None,
                new_version=None,
                is_breaking=False,
                change_type="added",
            )
        )
    return changes


# ---------------------------------------------------------------------------
# ManifestUpdater
# ---------------------------------------------------------------------------


class ManifestUpdater:
    """Computes diffs between two :class:`BundleManifest` instances.

    Usage::

        updater = ManifestUpdater()
        diff = updater.diff(old_manifest, new_manifest)
        if diff.has_breaking_changes:
            print("Breaking changes detected!")
        for change in diff.changes:
            print(change)
    """

    def diff(self, old: BundleManifest, new: BundleManifest) -> ManifestDiff:
        """Compute the diff between *old* and *new* manifests.

        Returns a :class:`ManifestDiff` containing exactly the components
        whose version (or filename / presence) changed.
        """
        changes: list[ComponentChange] = []

        # 1. Powers (versioned)
        old_powers = {p.name: p.version for p in old.components.powers}
        new_powers = {p.name: p.version for p in new.components.powers}
        changes.extend(_diff_versioned(old_powers, new_powers, "power"))

        # 2. MCP Servers (versioned)
        old_servers = {s.name: s.version for s in old.components.mcpServers}
        new_servers = {s.name: s.version for s in new.components.mcpServers}
        changes.extend(_diff_versioned(old_servers, new_servers, "mcp_server"))

        # 3. Skills (filename-based)
        old_skills = {s.name: s.filename for s in old.components.skills}
        new_skills = {s.name: s.filename for s in new.components.skills}
        changes.extend(_diff_filename_based(old_skills, new_skills, "skill"))

        # 4. Steering Files (filename-based)
        old_sf = {s.name: s.filename for s in old.components.steeringFiles}
        new_sf = {s.name: s.filename for s in new.components.steeringFiles}
        changes.extend(_diff_filename_based(old_sf, new_sf, "steering_file"))

        # 5. Pipeline Registries (name-only)
        old_pr = {r.name for r in old.components.pipelineRegistries}
        new_pr = {r.name for r in new.components.pipelineRegistries}
        changes.extend(_diff_name_only(old_pr, new_pr, "pipeline_registry"))

        return ManifestDiff(changes=changes)
