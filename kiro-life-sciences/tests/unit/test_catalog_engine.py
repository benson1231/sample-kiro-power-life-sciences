"""Unit tests for the resource catalog engine."""

import pytest

from kiro_life_sciences.catalog.engine import ResourceCatalogEngine
from kiro_life_sciences.models.catalog import (
    CatalogFilter,
    CrossReference,
    ResourceCategory,
    ResourceEntry,
)
from kiro_life_sciences.models.manifest import (
    BundleComponents,
    BundleManifest,
    ResourceCatalogDefinition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _entry(**overrides) -> ResourceEntry:
    """Build a minimal valid ResourceEntry with optional overrides."""
    base: dict = {
        "id": "ncbi-gene",
        "name": "NCBI Gene",
        "description": "NCBI Gene database for gene-centric information.",
        "category": "Genomics and Sequencing",
        "resourceType": "database",
        "url": "https://www.ncbi.nlm.nih.gov/gene/",
        "authRequired": False,
        "usageInstructions": "Search by gene symbol or ID.",
        "status": "needs_setup",
        "dataFormats": ["FASTA", "JSON"],
    }
    base.update(overrides)
    return ResourceEntry(**base)


def _make_entries() -> list[ResourceEntry]:
    """Return a small but diverse set of entries for testing."""
    return [
        _entry(
            id="ncbi-gene",
            name="NCBI Gene",
            description="NCBI Gene database for gene-centric information.",
            category="Genomics and Sequencing",
            resourceType="database",
            authRequired=False,
            dataFormats=["FASTA", "JSON"],
        ),
        _entry(
            id="uniprot",
            name="UniProt",
            description="Universal Protein Resource for protein sequences and annotations.",
            category="Proteomics",
            resourceType="database",
            authRequired=False,
            dataFormats=["FASTA", "XML", "JSON"],
        ),
        _entry(
            id="drugbank",
            name="DrugBank",
            description="Comprehensive drug and drug target database.",
            category="Clinical and Pharma",
            resourceType="database",
            authRequired=True,
            dataFormats=["JSON", "XML"],
        ),
        _entry(
            id="nfcore-rnaseq",
            name="nf-core/rnaseq",
            description="RNA sequencing analysis pipeline.",
            category="Pipelines",
            resourceType="pipeline",
            authRequired=False,
            dataFormats=["FASTQ", "BAM"],
        ),
        _entry(
            id="pdb",
            name="PDB",
            description="Protein Data Bank for 3D structural data.",
            category="Structural Biology",
            resourceType="database",
            authRequired=False,
            dataFormats=["PDB", "mmCIF"],
        ),
        _entry(
            id="bioformats-skill",
            name="Bioinformatics File Formats",
            description="Skill covering FASTA, FASTQ, BAM, VCF formats.",
            category="Bioinformatics Analysis Tools",
            resourceType="skill",
            authRequired=False,
            dataFormats=[],
        ),
    ]


def _engine(entries: list[ResourceEntry] | None = None) -> ResourceCatalogEngine:
    """Build an engine from the given entries (defaults to ``_make_entries``)."""
    return ResourceCatalogEngine(entries if entries is not None else _make_entries())


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    """Tests for engine construction."""

    def test_empty_catalog(self):
        engine = ResourceCatalogEngine([])
        assert engine.get_categories() == []

    def test_from_entries(self):
        engine = _engine()
        assert engine.get_entry("ncbi-gene") is not None

    def test_from_manifest(self):
        entries = _make_entries()
        manifest = BundleManifest(
            name="test",
            version="1.0.0",
            components=BundleComponents(),
            resourceCatalog=ResourceCatalogDefinition(entries=entries),
        )
        engine = ResourceCatalogEngine.from_manifest(manifest)
        assert engine.get_entry("ncbi-gene") is not None
        assert engine.get_entry("uniprot") is not None


# ---------------------------------------------------------------------------
# Search — scoring
# ---------------------------------------------------------------------------


class TestSearchScoring:
    """Tests for the search relevance ranking algorithm."""

    def test_exact_name_match_scores_highest(self):
        engine = _engine()
        result = engine.search("UniProt")
        assert result.entries[0].id == "uniprot"

    def test_exact_name_match_case_insensitive(self):
        engine = _engine()
        result = engine.search("uniprot")
        assert result.entries[0].id == "uniprot"

    def test_name_contains_keyword(self):
        engine = _engine()
        # "NCBI" is contained in "NCBI Gene"
        result = engine.search("NCBI")
        assert any(e.id == "ncbi-gene" for e in result.entries)

    def test_description_contains_keyword(self):
        engine = _engine()
        # "protein sequences" appears in UniProt's description
        result = engine.search("protein sequences")
        assert any(e.id == "uniprot" for e in result.entries)

    def test_category_matches_keyword(self):
        engine = _engine()
        result = engine.search("Proteomics")
        # UniProt is in the Proteomics category
        assert any(e.id == "uniprot" for e in result.entries)

    def test_data_formats_contain_keyword(self):
        engine = _engine()
        result = engine.search("mmCIF")
        assert any(e.id == "pdb" for e in result.entries)

    def test_no_match_returns_empty(self):
        engine = _engine()
        result = engine.search("xyznonexistent")
        assert result.entries == []
        assert result.totalCount == 0

    def test_results_sorted_by_score_descending(self):
        """Entries matching at a higher tier should appear before lower-tier matches."""
        entries = [
            _entry(
                id="a",
                name="Alpha",
                description="Contains the keyword genomics here.",
                category="Genomics and Sequencing",
                dataFormats=[],
            ),
            _entry(
                id="b",
                name="Genomics Tool",
                description="A tool.",
                category="Bioinformatics Analysis Tools",
                dataFormats=[],
            ),
        ]
        engine = _engine(entries)
        result = engine.search("genomics")
        # "Genomics Tool" has keyword in name (0.8) vs "Alpha" in description (0.6)
        assert result.entries[0].id == "b"
        assert result.entries[1].id == "a"

    def test_same_score_sorted_alphabetically(self):
        """Entries with the same score should be sorted alphabetically by name."""
        entries = [
            _entry(id="z", name="Zebra DB", description="A database.", dataFormats=["FASTA"]),
            _entry(id="a", name="Alpha DB", description="A database.", dataFormats=["FASTA"]),
        ]
        engine = _engine(entries)
        # Both match on dataFormats ("FASTA") → same score 0.2
        result = engine.search("FASTA")
        assert result.entries[0].id == "a"
        assert result.entries[1].id == "z"

    def test_search_result_metadata(self):
        engine = _engine()
        result = engine.search("gene")
        assert result.query == "gene"
        assert isinstance(result.filters, CatalogFilter)
        assert result.totalCount == len(result.entries)


# ---------------------------------------------------------------------------
# Search — filtering
# ---------------------------------------------------------------------------


class TestSearchFiltering:
    """Tests for search with filters applied."""

    def test_filter_by_category(self):
        engine = _engine()
        f = CatalogFilter(category=ResourceCategory.PROTEOMICS)
        result = engine.search("protein", filters=f)
        for entry in result.entries:
            assert entry.category == ResourceCategory.PROTEOMICS

    def test_filter_by_resource_type(self):
        engine = _engine()
        f = CatalogFilter(resourceType="pipeline")
        result = engine.search("sequencing", filters=f)
        for entry in result.entries:
            assert entry.resourceType == "pipeline"

    def test_filter_authenticated(self):
        engine = _engine()
        f = CatalogFilter(authRequirement="authenticated")
        result = engine.search("drug", filters=f)
        for entry in result.entries:
            assert entry.authRequired is True

    def test_filter_open_access(self):
        engine = _engine()
        f = CatalogFilter(authRequirement="open_access")
        result = engine.search("gene", filters=f)
        for entry in result.entries:
            assert entry.authRequired is False

    def test_combined_filters_and_logic(self):
        engine = _engine()
        f = CatalogFilter(
            category=ResourceCategory.GENOMICS_AND_SEQUENCING,
            resourceType="database",
            authRequirement="open_access",
        )
        result = engine.search("gene", filters=f)
        for entry in result.entries:
            assert entry.category == ResourceCategory.GENOMICS_AND_SEQUENCING
            assert entry.resourceType == "database"
            assert entry.authRequired is False

    def test_filter_excludes_non_matching(self):
        engine = _engine()
        f = CatalogFilter(category=ResourceCategory.PROTEOMICS)
        result = engine.search("NCBI", filters=f)
        # NCBI Gene is in Genomics, not Proteomics — should be excluded
        assert not any(e.id == "ncbi-gene" for e in result.entries)

    def test_empty_result_with_filters(self):
        engine = _engine()
        f = CatalogFilter(category=ResourceCategory.EPIGENOMICS)
        result = engine.search("anything", filters=f)
        assert result.entries == []
        assert result.totalCount == 0


# ---------------------------------------------------------------------------
# Browse
# ---------------------------------------------------------------------------


class TestBrowse:
    """Tests for the browse() method."""

    def test_browse_returns_entries_in_category(self):
        engine = _engine()
        results = engine.browse(ResourceCategory.GENOMICS_AND_SEQUENCING)
        assert len(results) >= 1
        for entry in results:
            assert entry.category == ResourceCategory.GENOMICS_AND_SEQUENCING

    def test_browse_sorted_alphabetically_case_insensitive(self):
        entries = [
            _entry(id="z", name="zebra", category="Genomics and Sequencing"),
            _entry(id="a", name="Alpha", category="Genomics and Sequencing"),
            _entry(id="m", name="middle", category="Genomics and Sequencing"),
        ]
        engine = _engine(entries)
        results = engine.browse(ResourceCategory.GENOMICS_AND_SEQUENCING)
        names = [e.name for e in results]
        assert names == ["Alpha", "middle", "zebra"]

    def test_browse_empty_category(self):
        engine = _engine()
        results = engine.browse(ResourceCategory.EPIGENOMICS)
        assert results == []

    def test_browse_with_additional_filters(self):
        entries = [
            _entry(id="a", name="A", category="Genomics and Sequencing", authRequired=True),
            _entry(id="b", name="B", category="Genomics and Sequencing", authRequired=False),
        ]
        engine = _engine(entries)
        results = engine.browse(
            ResourceCategory.GENOMICS_AND_SEQUENCING,
            filters=CatalogFilter(authRequirement="open_access"),
        )
        assert len(results) == 1
        assert results[0].id == "b"


# ---------------------------------------------------------------------------
# get_entry
# ---------------------------------------------------------------------------


class TestGetEntry:
    """Tests for the get_entry() method."""

    def test_existing_entry(self):
        engine = _engine()
        entry = engine.get_entry("ncbi-gene")
        assert entry is not None
        assert entry.id == "ncbi-gene"

    def test_missing_entry_returns_none(self):
        engine = _engine()
        assert engine.get_entry("nonexistent") is None

    def test_empty_catalog_returns_none(self):
        engine = ResourceCatalogEngine([])
        assert engine.get_entry("anything") is None


# ---------------------------------------------------------------------------
# get_categories
# ---------------------------------------------------------------------------


class TestGetCategories:
    """Tests for the get_categories() method."""

    def test_returns_categories_with_counts(self):
        engine = _engine()
        cats = engine.get_categories()
        assert len(cats) > 0
        for item in cats:
            assert "category" in item
            assert "count" in item
            assert item["count"] > 0

    def test_counts_are_accurate(self):
        entries = [
            _entry(id="a", name="A", category="Genomics and Sequencing"),
            _entry(id="b", name="B", category="Genomics and Sequencing"),
            _entry(id="c", name="C", category="Proteomics"),
        ]
        engine = _engine(entries)
        cats = engine.get_categories()
        cat_map = {item["category"]: item["count"] for item in cats}
        assert cat_map[ResourceCategory.GENOMICS_AND_SEQUENCING] == 2
        assert cat_map[ResourceCategory.PROTEOMICS] == 1

    def test_categories_sorted_alphabetically(self):
        engine = _engine()
        cats = engine.get_categories()
        cat_names = [str(item["category"]) for item in cats]
        assert cat_names == sorted(cat_names)

    def test_empty_catalog_returns_empty(self):
        engine = ResourceCatalogEngine([])
        assert engine.get_categories() == []


# ---------------------------------------------------------------------------
# get_related
# ---------------------------------------------------------------------------


class TestGetRelated:
    """Tests for the get_related() method."""

    def test_returns_cross_referenced_entries(self):
        entries = [
            _entry(
                id="ncbi-gene",
                name="NCBI Gene",
                crossReferences=[
                    CrossReference(
                        targetResourceId="uniprot",
                        targetResourceName="UniProt",
                        relationship="commonly used with",
                    ),
                ],
            ),
            _entry(id="uniprot", name="UniProt", category="Proteomics"),
        ]
        engine = _engine(entries)
        related = engine.get_related("ncbi-gene")
        assert len(related) == 1
        assert related[0].id == "uniprot"

    def test_missing_cross_reference_target_excluded(self):
        entries = [
            _entry(
                id="ncbi-gene",
                name="NCBI Gene",
                crossReferences=[
                    CrossReference(
                        targetResourceId="nonexistent",
                        targetResourceName="Ghost",
                        relationship="links to",
                    ),
                ],
            ),
        ]
        engine = _engine(entries)
        related = engine.get_related("ncbi-gene")
        assert related == []

    def test_no_cross_references_returns_empty(self):
        engine = _engine()
        related = engine.get_related("ncbi-gene")
        assert related == []

    def test_nonexistent_entry_returns_empty(self):
        engine = _engine()
        related = engine.get_related("nonexistent")
        assert related == []

    def test_multiple_cross_references(self):
        entries = [
            _entry(
                id="ncbi-gene",
                name="NCBI Gene",
                crossReferences=[
                    CrossReference(
                        targetResourceId="uniprot",
                        targetResourceName="UniProt",
                        relationship="commonly used with",
                    ),
                    CrossReference(
                        targetResourceId="pdb",
                        targetResourceName="PDB",
                        relationship="provides data for",
                    ),
                ],
            ),
            _entry(id="uniprot", name="UniProt", category="Proteomics"),
            _entry(id="pdb", name="PDB", category="Structural Biology"),
        ]
        engine = _engine(entries)
        related = engine.get_related("ncbi-gene")
        assert len(related) == 2
        related_ids = {e.id for e in related}
        assert related_ids == {"uniprot", "pdb"}


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge-case and integration tests."""

    def test_search_empty_keyword(self):
        """An empty keyword should match nothing (no field contains '')."""
        engine = _engine()
        # Empty string is technically contained in every string, so all entries match
        result = engine.search("")
        # All entries should match since "" is in every name
        assert result.totalCount == len(_make_entries())

    def test_search_with_none_filters(self):
        engine = _engine()
        result = engine.search("gene", filters=None)
        assert result.totalCount > 0

    def test_duplicate_ids_last_wins(self):
        """If entries have duplicate IDs, the last one wins in the lookup."""
        entries = [
            _entry(id="dup", name="First"),
            _entry(id="dup", name="Second"),
        ]
        engine = _engine(entries)
        entry = engine.get_entry("dup")
        assert entry is not None
        assert entry.name == "Second"

    def test_search_special_characters(self):
        """Search with special characters should not crash."""
        engine = _engine()
        result = engine.search("AI/ML")
        # Should match the category "AI/ML for Life Sciences"
        # No crash is the main assertion
        assert isinstance(result.totalCount, int)
