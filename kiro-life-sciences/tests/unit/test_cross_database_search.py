"""Unit tests for the cross-database search skill."""

from __future__ import annotations

import asyncio

import pytest

from kiro_life_sciences.skills.cross_database_search import (
    CrossDatabaseSearch,
    CrossDatabaseSearchResult,
    DatabaseGroupResult,
    SearchType,
    UnavailableDatabase,
    UnavailableReason,
    SEARCH_TYPE_DATABASE_MAP,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


def _make_query_fn(results: list | None = None, *, raise_exc: Exception | None = None, delay: float = 0.0):
    """Create a mock async query function."""

    async def _fn(query: str) -> list:
        if delay:
            await asyncio.sleep(delay)
        if raise_exc is not None:
            raise raise_exc
        return results if results is not None else []

    return _fn


# ---------------------------------------------------------------------------
# Tests: search type → database mapping
# ---------------------------------------------------------------------------


class TestSearchTypeDatabaseMapping:
    """Verify the static mapping from search types to databases."""

    def test_all_search_types_have_mappings(self):
        for st in SearchType:
            assert st.value in SEARCH_TYPE_DATABASE_MAP

    def test_gene_mapping_contains_expected_databases(self):
        db_names = [db for db, _ in SEARCH_TYPE_DATABASE_MAP[SearchType.GENE]]
        assert "NCBI Gene" in db_names
        assert "UniProt" in db_names
        assert "Ensembl" in db_names
        assert "ClinVar" in db_names

    def test_drug_mapping_contains_expected_databases(self):
        db_names = [db for db, _ in SEARCH_TYPE_DATABASE_MAP[SearchType.DRUG]]
        assert "DrugBank" in db_names
        assert "ChEMBL" in db_names
        assert "PubChem" in db_names

    def test_protein_mapping_contains_expected_databases(self):
        db_names = [db for db, _ in SEARCH_TYPE_DATABASE_MAP[SearchType.PROTEIN]]
        assert "UniProt" in db_names
        assert "PDB" in db_names
        assert "AlphaFold DB" in db_names

    def test_species_mapping_contains_expected_databases(self):
        db_names = [db for db, _ in SEARCH_TYPE_DATABASE_MAP[SearchType.SPECIES]]
        assert "GBIF" in db_names
        assert "IUCN Red List" in db_names

    def test_metabolite_mapping_contains_expected_databases(self):
        db_names = [db for db, _ in SEARCH_TYPE_DATABASE_MAP[SearchType.METABOLITE]]
        assert "HMDB" in db_names
        assert "MassBank" in db_names

    def test_cell_type_mapping_contains_expected_databases(self):
        db_names = [db for db, _ in SEARCH_TYPE_DATABASE_MAP[SearchType.CELL_TYPE]]
        assert "CellxGene" in db_names
        assert "Allen Brain Atlas" in db_names

    def test_no_duplicate_databases_per_search_type(self):
        for st, mapping in SEARCH_TYPE_DATABASE_MAP.items():
            db_names = [db for db, _ in mapping]
            assert len(db_names) == len(set(db_names)), f"Duplicate databases in {st}"

    def test_get_databases_for_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown search type"):
            CrossDatabaseSearch.get_databases_for_search_type("unknown_type")


# ---------------------------------------------------------------------------
# Tests: search execution
# ---------------------------------------------------------------------------


class TestCrossDatabaseSearch:
    """Test the CrossDatabaseSearch.search() method."""

    def test_all_servers_unavailable(self):
        """When no servers are installed, all databases are unavailable."""
        searcher = CrossDatabaseSearch(available_servers=set())
        result = _run(searcher.search("BRCA1", SearchType.GENE))

        assert isinstance(result, CrossDatabaseSearchResult)
        assert result.query == "BRCA1"
        assert result.search_type == SearchType.GENE
        assert len(result.results) == 0
        expected_db_count = len(SEARCH_TYPE_DATABASE_MAP[SearchType.GENE])
        assert len(result.unavailable_databases) == expected_db_count
        for udb in result.unavailable_databases:
            assert udb.reason == UnavailableReason.NOT_INSTALLED

    def test_successful_query(self):
        """Databases with registered query functions return results."""
        searcher = CrossDatabaseSearch(
            available_servers={"life-sciences-cellbiology", "life-sciences-neuroscience"},
        )
        searcher.register_query_fn(
            "CellxGene",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "1", "name": "T cell"}]),
        )
        searcher.register_query_fn(
            "Single Cell Expression Atlas",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "2", "name": "B cell"}]),
        )
        searcher.register_query_fn(
            "Cell Atlas",
            "life-sciences-cellbiology",
            _make_query_fn([]),
        )
        searcher.register_query_fn(
            "Allen Brain Atlas",
            "life-sciences-neuroscience",
            _make_query_fn([{"id": "3", "name": "Neuron"}]),
        )

        result = _run(searcher.search("T cell", SearchType.CELL_TYPE))

        assert len(result.results) == 4
        assert len(result.unavailable_databases) == 0

        # Check that CellxGene returned the expected entry
        cellxgene = next(r for r in result.results if r.database == "CellxGene")
        assert cellxgene.result_count == 1
        assert cellxgene.entries[0]["name"] == "T cell"

    def test_partial_failure_returns_successful_results(self):
        """When some databases fail, results from successful ones are still returned."""
        searcher = CrossDatabaseSearch(
            available_servers={"life-sciences-cellbiology", "life-sciences-neuroscience"},
        )
        searcher.register_query_fn(
            "CellxGene",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "1"}]),
        )
        searcher.register_query_fn(
            "Single Cell Expression Atlas",
            "life-sciences-cellbiology",
            _make_query_fn(raise_exc=RuntimeError("API down")),
        )
        searcher.register_query_fn(
            "Cell Atlas",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "2"}]),
        )
        searcher.register_query_fn(
            "Allen Brain Atlas",
            "life-sciences-neuroscience",
            _make_query_fn([{"id": "3"}]),
        )

        result = _run(searcher.search("neuron", SearchType.CELL_TYPE))

        # 3 successful, 1 failed
        assert len(result.results) == 3
        assert len(result.unavailable_databases) == 1
        assert result.unavailable_databases[0].database == "Single Cell Expression Atlas"
        assert result.unavailable_databases[0].reason == UnavailableReason.API_ERROR

    def test_timeout_handling(self):
        """Databases that exceed the timeout are recorded as unavailable."""
        searcher = CrossDatabaseSearch(
            available_servers={"life-sciences-cellbiology", "life-sciences-neuroscience"},
            timeout=0.05,  # 50ms timeout
        )
        searcher.register_query_fn(
            "CellxGene",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "1"}]),
        )
        searcher.register_query_fn(
            "Single Cell Expression Atlas",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "2"}], delay=1.0),  # Will timeout
        )
        searcher.register_query_fn(
            "Cell Atlas",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "3"}]),
        )
        searcher.register_query_fn(
            "Allen Brain Atlas",
            "life-sciences-neuroscience",
            _make_query_fn([{"id": "4"}]),
        )

        result = _run(searcher.search("cell", SearchType.CELL_TYPE))

        assert len(result.results) == 3
        assert len(result.unavailable_databases) == 1
        timeout_db = result.unavailable_databases[0]
        assert timeout_db.database == "Single Cell Expression Atlas"
        assert timeout_db.reason == UnavailableReason.TIMEOUT

    def test_missing_query_fn_treated_as_credentials_missing(self):
        """Server installed but no query fn registered → credentials_missing."""
        searcher = CrossDatabaseSearch(
            available_servers={"life-sciences-cellbiology", "life-sciences-neuroscience"},
        )
        # Don't register any query functions

        result = _run(searcher.search("cell", SearchType.CELL_TYPE))

        assert len(result.results) == 0
        assert len(result.unavailable_databases) == 4
        for udb in result.unavailable_databases:
            assert udb.reason == UnavailableReason.CREDENTIALS_MISSING

    def test_mixed_installed_and_not_installed(self):
        """Mix of installed and not-installed servers."""
        searcher = CrossDatabaseSearch(
            available_servers={"life-sciences-cellbiology"},
            # life-sciences-neuroscience is NOT installed
        )
        searcher.register_query_fn(
            "CellxGene",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "1"}]),
        )
        searcher.register_query_fn(
            "Single Cell Expression Atlas",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "2"}]),
        )
        searcher.register_query_fn(
            "Cell Atlas",
            "life-sciences-cellbiology",
            _make_query_fn([{"id": "3"}]),
        )

        result = _run(searcher.search("cell", SearchType.CELL_TYPE))

        # 3 successful from cellbiology, 1 unavailable from neuroscience
        assert len(result.results) == 3
        assert len(result.unavailable_databases) == 1
        assert result.unavailable_databases[0].database == "Allen Brain Atlas"
        assert result.unavailable_databases[0].reason == UnavailableReason.NOT_INSTALLED

    def test_result_databases_are_unique(self):
        """No database should appear more than once in results."""
        searcher = CrossDatabaseSearch(
            available_servers={"life-sciences-genomics", "life-sciences-proteomics",
                               "life-sciences-clinical", "life-sciences-ontologies",
                               "life-sciences-pathways", "life-sciences-neuroscience",
                               "life-sciences-immunology", "life-sciences-cellbiology"},
        )
        # Register query fns for all gene databases
        for db_name, server_name in SEARCH_TYPE_DATABASE_MAP[SearchType.GENE]:
            searcher.register_query_fn(db_name, server_name, _make_query_fn([]))

        result = _run(searcher.search("BRCA1", SearchType.GENE))

        result_dbs = [r.database for r in result.results]
        assert len(result_dbs) == len(set(result_dbs)), "Duplicate databases in results"
