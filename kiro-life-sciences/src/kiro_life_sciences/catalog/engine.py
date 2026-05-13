"""Resource catalog engine — search, browse, and filter resource entries.

The engine builds an in-memory index from a list of :class:`ResourceEntry`
objects (typically loaded from the bundle manifest) and exposes operations
defined in the design document under *Components and Interfaces §2 —
Resource Catalog Engine*.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from kiro_life_sciences.models.catalog import (
    CatalogFilter,
    CatalogSearchResult,
    ResourceCategory,
    ResourceEntry,
)

if TYPE_CHECKING:
    from kiro_life_sciences.models.manifest import BundleManifest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_NO_RESULTS_MESSAGE = (
    "No resources matched the criteria. Try broadening your search or removing filters."
)

# Relevance score tiers (design doc §2)
_SCORE_EXACT_NAME = 1.0
_SCORE_NAME_CONTAINS = 0.8
_SCORE_DESCRIPTION_CONTAINS = 0.6
_SCORE_CATEGORY_MATCHES = 0.4
_SCORE_TAGS_FORMATS_CONTAIN = 0.2


class ResourceCatalogEngine:
    """In-memory resource catalog with search, browse, and filter support.

    Parameters
    ----------
    entries:
        The full list of :class:`ResourceEntry` objects to index.
    """

    def __init__(self, entries: list[ResourceEntry]) -> None:
        self._entries = list(entries)
        # Build a lookup by id for O(1) access
        self._by_id: dict[str, ResourceEntry] = {e.id: e for e in self._entries}

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_manifest(cls, manifest: BundleManifest) -> ResourceCatalogEngine:
        """Create a catalog engine from a :class:`BundleManifest`.

        The manifest's ``resourceCatalog.entries`` list is used directly.
        """
        return cls(manifest.resourceCatalog.entries)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        keyword: str,
        filters: CatalogFilter | None = None,
    ) -> CatalogSearchResult:
        """Search entries by *keyword* with optional *filters*.

        Scoring algorithm (design doc §2):
        1. Exact name match → 1.0
        2. Name contains keyword → 0.8
        3. Description contains keyword → 0.6
        4. Category matches keyword → 0.4
        5. Tags / data formats contain keyword → 0.2

        Results are sorted by score descending, then alphabetically by name
        (case-insensitive) within the same score.  Entries that do not match
        any field are excluded.  Active filters are applied **before** scoring
        so that irrelevant entries are never returned.
        """
        effective_filters = filters or CatalogFilter()
        candidates = self._apply_filters(self._entries, effective_filters)

        scored: list[tuple[float, ResourceEntry]] = []
        kw_lower = keyword.lower()

        for entry in candidates:
            score = self._score_entry(entry, kw_lower)
            if score > 0:
                scored.append((score, entry))

        # Sort: highest score first, then alphabetically by name (case-insensitive)
        scored.sort(key=lambda pair: (-pair[0], pair[1].name.lower()))

        matched_entries = [entry for _, entry in scored]

        return CatalogSearchResult(
            entries=matched_entries,
            totalCount=len(matched_entries),
            query=keyword,
            filters=effective_filters,
        )

    # ------------------------------------------------------------------
    # Browse
    # ------------------------------------------------------------------

    def browse(
        self,
        category: ResourceCategory,
        filters: CatalogFilter | None = None,
    ) -> list[ResourceEntry]:
        """Return entries in *category*, sorted alphabetically by name (case-insensitive).

        An optional *filters* argument can further narrow results (the
        category field in the filter is ignored — the explicit *category*
        parameter takes precedence).
        """
        # Start with entries matching the requested category
        results = [e for e in self._entries if e.category == category]

        # Apply additional filters (but override category to avoid conflict)
        if filters is not None:
            override = filters.model_copy(update={"category": None})
            results = self._apply_filters(results, override)

        results.sort(key=lambda e: e.name.lower())
        return results

    # ------------------------------------------------------------------
    # Single-entry lookup
    # ------------------------------------------------------------------

    def get_entry(self, id: str) -> ResourceEntry | None:
        """Return the entry with the given *id*, or ``None`` if not found."""
        return self._by_id.get(id)

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def get_categories(self) -> list[dict]:
        """Return ``[{category, count}]`` for every category that has entries.

        Categories are sorted alphabetically by their string value.
        """
        counts: dict[ResourceCategory, int] = {}
        for entry in self._entries:
            counts[entry.category] = counts.get(entry.category, 0) + 1

        return sorted(
            [{"category": cat, "count": cnt} for cat, cnt in counts.items()],
            key=lambda d: str(d["category"]),
        )

    # ------------------------------------------------------------------
    # Related resources
    # ------------------------------------------------------------------

    def get_related(self, id: str) -> list[ResourceEntry]:
        """Return entries cross-referenced by the entry with the given *id*.

        Only cross-references whose ``targetResourceId`` exists in the catalog
        are included.  Returns an empty list if the entry is not found or has
        no cross-references.
        """
        entry = self._by_id.get(id)
        if entry is None:
            return []

        related: list[ResourceEntry] = []
        for xref in entry.crossReferences:
            target = self._by_id.get(xref.targetResourceId)
            if target is not None:
                related.append(target)
        return related

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _score_entry(entry: ResourceEntry, kw_lower: str) -> float:
        """Compute the highest relevance score for *entry* against *kw_lower*.

        The score is the **maximum** across all matching tiers (an entry that
        matches both name-contains and description-contains gets 0.8, not the
        sum).
        """
        name_lower = entry.name.lower()

        # Tier 1 — exact name match
        if name_lower == kw_lower:
            return _SCORE_EXACT_NAME

        # Tier 2 — name contains keyword
        if kw_lower in name_lower:
            return _SCORE_NAME_CONTAINS

        # Tier 3 — description contains keyword
        if kw_lower in entry.description.lower():
            return _SCORE_DESCRIPTION_CONTAINS

        # Tier 4 — category matches keyword
        if kw_lower in entry.category.lower():
            return _SCORE_CATEGORY_MATCHES

        # Tier 5 — tags / data formats contain keyword
        for fmt in entry.dataFormats:
            if kw_lower in fmt.lower():
                return _SCORE_TAGS_FORMATS_CONTAIN

        return 0.0

    @staticmethod
    def _apply_filters(
        entries: list[ResourceEntry],
        filters: CatalogFilter,
    ) -> list[ResourceEntry]:
        """Return entries that satisfy **all** active filter criteria (AND logic)."""
        result = entries

        if filters.category is not None:
            result = [e for e in result if e.category == filters.category]

        if filters.resourceType is not None:
            result = [e for e in result if e.resourceType == filters.resourceType]

        if filters.authRequirement is not None:
            if filters.authRequirement == "authenticated":
                result = [e for e in result if e.authRequired is True]
            elif filters.authRequirement == "open_access":
                result = [e for e in result if e.authRequired is False]

        return result
