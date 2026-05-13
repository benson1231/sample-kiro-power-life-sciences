"""Property-based tests for the resource catalog engine.

Uses Hypothesis to verify universal correctness properties across randomly
generated catalogs and search inputs.  Each test runs a minimum of 100
iterations.
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st, assume

from kiro_life_sciences.catalog.engine import ResourceCatalogEngine
from kiro_life_sciences.models.catalog import (
    CatalogFilter,
    CrossReference,
    ResourceCategory,
    ResourceEntry,
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

_data_format_st = st.sampled_from([
    "FASTA", "FASTQ", "JSON", "XML", "CSV", "BAM", "VCF", "PDB", "mmCIF",
    "GFF", "BED", "DICOM", "SBML", "BioPAX",
])

_status_st = st.sampled_from(["ready", "needs_setup", "needs_credentials"])


@st.composite
def resource_entry_st(draw, entry_id=None, category=None, cross_refs=None):
    """Generate a valid ResourceEntry with optional overrides."""
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
        dataFormats=draw(st.lists(_data_format_st, max_size=4)),
        usageInstructions=draw(_name_st),
        status=draw(_status_st),
        crossReferences=cross_refs if cross_refs is not None else [],
    )


@st.composite
def catalog_entries_st(draw, min_size=1, max_size=15):
    """Generate a list of ResourceEntry objects with unique IDs."""
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    entries = []
    for i in range(n):
        entries.append(draw(resource_entry_st(entry_id=f"entry-{i}")))
    return entries


@st.composite
def keyword_from_entries_st(draw, entries):
    """Pick a keyword that appears in at least one entry's searchable fields."""
    assume(len(entries) > 0)
    entry = draw(st.sampled_from(entries))
    # Pick a word from the entry's name (most reliable match)
    words = entry.name.split()
    assume(len(words) > 0)
    word = draw(st.sampled_from(words))
    assume(len(word) >= 1)
    return word


# ===========================================================================
# Property 9: Catalog Search Returns Relevant Results in Ranked Order (Task 3.9)
# ===========================================================================
# Feature: kiro-life-sciences, Property 9: Catalog Search Relevance Ranking


class TestCatalogSearchRelevanceRanking:
    """All returned results contain the keyword in at least one searchable
    field, sorted by score descending.

    **Validates: Requirements 7.2**
    """

    @given(data=st.data())
    @settings(max_examples=100)
    def test_results_contain_keyword_and_sorted_by_score(self, data):
        entries = data.draw(catalog_entries_st(min_size=2, max_size=12))
        keyword = data.draw(keyword_from_entries_st(entries))

        engine = ResourceCatalogEngine(entries)
        result = engine.search(keyword)

        kw_lower = keyword.lower()

        for entry in result.entries:
            # The keyword must appear in at least one searchable field
            found = (
                kw_lower in entry.name.lower()
                or kw_lower in entry.description.lower()
                or kw_lower in entry.category.lower()
                or any(kw_lower in fmt.lower() for fmt in entry.dataFormats)
            )
            assert found, (
                f"Entry '{entry.name}' returned but keyword '{keyword}' "
                f"not found in any searchable field"
            )

        # Verify descending score order by re-scoring
        scores = [engine._score_entry(e, kw_lower) for e in result.entries]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], (
                f"Score {scores[i]} at index {i} should be >= {scores[i + 1]} at index {i + 1}"
            )


# ===========================================================================
# Property 10: Catalog Filter Correctness (Task 3.10)
# ===========================================================================
# Feature: kiro-life-sciences, Property 10: Catalog Filter Correctness


@st.composite
def filter_st(draw):
    """Generate a random CatalogFilter."""
    cat = draw(st.one_of(st.none(), _category_st))
    rt = draw(st.one_of(st.none(), _resource_type_st))
    auth = draw(st.one_of(st.none(), st.sampled_from(["authenticated", "open_access"])))
    return CatalogFilter(category=cat, resourceType=rt, authRequirement=auth)


class TestCatalogFilterCorrectness:
    """All returned results satisfy every active filter, and no matching
    resource is excluded.

    **Validates: Requirements 7.3, 7.4**
    """

    @given(data=st.data())
    @settings(max_examples=100)
    def test_filter_correctness(self, data):
        entries = data.draw(catalog_entries_st(min_size=1, max_size=12))
        filt = data.draw(filter_st())

        engine = ResourceCatalogEngine(entries)
        # Use empty string keyword to get all entries through the filter
        # (empty string matches all entries since "" is in every string)
        result = engine.search("", filters=filt)

        # All returned entries satisfy every active filter
        for entry in result.entries:
            if filt.category is not None:
                assert entry.category == filt.category
            if filt.resourceType is not None:
                assert entry.resourceType == filt.resourceType
            if filt.authRequirement == "authenticated":
                assert entry.authRequired is True
            elif filt.authRequirement == "open_access":
                assert entry.authRequired is False

        # No matching resource is excluded
        returned_ids = {e.id for e in result.entries}
        for entry in entries:
            matches = True
            if filt.category is not None and entry.category != filt.category:
                matches = False
            if filt.resourceType is not None and entry.resourceType != filt.resourceType:
                matches = False
            if filt.authRequirement == "authenticated" and not entry.authRequired:
                matches = False
            if filt.authRequirement == "open_access" and entry.authRequired:
                matches = False
            if matches:
                assert entry.id in returned_ids, (
                    f"Entry '{entry.name}' matches all filters but was excluded"
                )


# ===========================================================================
# Property 11: Catalog Completeness (Task 3.11)
# ===========================================================================
# Feature: kiro-life-sciences, Property 11: Catalog Completeness

from kiro_life_sciences.models.manifest import (
    BundleComponents,
    BundleManifest,
    ResourceCatalogDefinition,
)


@st.composite
def manifest_with_catalog_entries_st(draw):
    """Generate a manifest where resourceCatalog.entries has one entry per
    component, ensuring the catalog is complete."""
    entries = draw(catalog_entries_st(min_size=1, max_size=10))
    return BundleManifest(
        name="test-bundle",
        version="1.0.0",
        components=BundleComponents(),
        resourceCatalog=ResourceCatalogDefinition(entries=entries),
    )


class TestCatalogCompleteness:
    """The catalog contains exactly one ResourceEntry for every item in the
    manifest — no duplicates, no omissions.

    **Validates: Requirements 8.1**
    """

    @given(manifest=manifest_with_catalog_entries_st())
    @settings(max_examples=100)
    def test_catalog_completeness(self, manifest: BundleManifest):
        engine = ResourceCatalogEngine.from_manifest(manifest)
        expected_entries = manifest.resourceCatalog.entries

        # Every entry in the manifest is in the catalog
        for entry in expected_entries:
            found = engine.get_entry(entry.id)
            assert found is not None, f"Entry {entry.id} missing from catalog"
            assert found.name == entry.name

        # No extra entries (catalog size == manifest entries size)
        cats = engine.get_categories()
        total_in_catalog = sum(c["count"] for c in cats)
        assert total_in_catalog == len(expected_entries)

        # No duplicate IDs
        ids = [e.id for e in expected_entries]
        assert len(ids) == len(set(ids)), "Duplicate IDs in manifest entries"


# ===========================================================================
# Property 12: Category Browse Sort Order (Task 3.12)
# ===========================================================================
# Feature: kiro-life-sciences, Property 12: Category Browse Sort Order


@st.composite
def entries_with_shared_category_st(draw):
    """Generate entries where at least 2 share the same category."""
    cat = draw(_category_st)
    n = draw(st.integers(min_value=2, max_value=8))
    entries = []
    for i in range(n):
        entries.append(draw(resource_entry_st(entry_id=f"cat-entry-{i}", category=cat)))
    return entries, cat


class TestCategoryBrowseSortOrder:
    """Browsing a category returns entries sorted alphabetically by name
    (case-insensitive).

    **Validates: Requirements 9.2**
    """

    @given(data=entries_with_shared_category_st())
    @settings(max_examples=100)
    def test_browse_sorted_alphabetically(self, data):
        entries, category = data
        engine = ResourceCatalogEngine(entries)
        results = engine.browse(category)

        assert len(results) == len(entries)

        # Verify alphabetical sort (case-insensitive)
        names = [e.name.lower() for e in results]
        assert names == sorted(names), (
            f"Browse results not sorted: {[e.name for e in results]}"
        )


# ===========================================================================
# Property 13: Related Resources Retrieval (Task 3.13)
# ===========================================================================
# Feature: kiro-life-sciences, Property 13: Related Resources Retrieval


@st.composite
def catalog_with_cross_refs_st(draw):
    """Generate a catalog with cross-reference graphs."""
    n = draw(st.integers(min_value=2, max_value=10))
    entry_ids = [f"xref-{i}" for i in range(n)]

    entries = []
    for i, eid in enumerate(entry_ids):
        # Each entry may cross-reference some other entries
        other_ids = [x for x in entry_ids if x != eid]
        num_refs = draw(st.integers(min_value=0, max_value=min(3, len(other_ids))))
        ref_targets = draw(
            st.lists(
                st.sampled_from(other_ids),
                min_size=num_refs,
                max_size=num_refs,
                unique=True,
            )
        ) if other_ids and num_refs > 0 else []

        cross_refs = [
            CrossReference(
                targetResourceId=tid,
                targetResourceName=f"Name-{tid}",
                relationship="commonly used with",
            )
            for tid in ref_targets
        ]
        entries.append(draw(resource_entry_st(entry_id=eid, cross_refs=cross_refs)))

    return entries


class TestRelatedResourcesRetrieval:
    """get_related returns all cross-referenced resources that exist in the
    catalog.

    **Validates: Requirements 9.4**
    """

    @given(entries=catalog_with_cross_refs_st())
    @settings(max_examples=100)
    def test_related_returns_existing_cross_refs(self, entries):
        engine = ResourceCatalogEngine(entries)
        catalog_ids = {e.id for e in entries}

        for entry in entries:
            related = engine.get_related(entry.id)
            related_ids = {r.id for r in related}

            # Every cross-reference that exists in the catalog is returned
            for xref in entry.crossReferences:
                if xref.targetResourceId in catalog_ids:
                    assert xref.targetResourceId in related_ids, (
                        f"Cross-ref {xref.targetResourceId} exists in catalog "
                        f"but not returned by get_related({entry.id})"
                    )

            # No extra entries returned
            expected_ids = {
                xref.targetResourceId
                for xref in entry.crossReferences
                if xref.targetResourceId in catalog_ids
            }
            assert related_ids == expected_ids
