"""Integration tests for cross-database search.

Tests cross-database search with mocked databases and graceful degradation
with simulated failures.

**Validates: Requirements 54.1-54.8**
"""

from __future__ import annotations

import asyncio

import pytest

from kiro_life_sciences.skills.cross_database_search import (
    CrossDatabaseSearch,
    SearchType,
    UnavailableReason,
)


class TestCrossDatabaseSearchIntegration:
    async def test_gene_search_with_mocked_databases(self):
        """Search across multiple mocked gene databases."""
        available = {
            "life-sciences-genomics",
            "life-sciences-proteomics",
        }
        search = CrossDatabaseSearch(available, timeout=5.0)

        # Register mock query functions
        async def mock_ncbi(query: str):
            return [{"gene": query, "source": "NCBI"}]

        async def mock_uniprot(query: str):
            return [{"protein": query, "source": "UniProt"}]

        search.register_query_fn("NCBI Gene", "life-sciences-genomics", mock_ncbi)
        search.register_query_fn("UniProt", "life-sciences-proteomics", mock_uniprot)

        result = await search.search("BRCA1", SearchType.GENE)

        assert result.query == "BRCA1"
        assert result.search_type == SearchType.GENE

        # Should have results from registered databases
        result_dbs = {r.database for r in result.results}
        assert "NCBI Gene" in result_dbs
        assert "UniProt" in result_dbs

        # Uninstalled servers should be in unavailable
        unavail_dbs = {u.database for u in result.unavailable_databases}
        # Some databases map to servers not in available set
        for u in result.unavailable_databases:
            assert u.reason in (
                UnavailableReason.NOT_INSTALLED,
                UnavailableReason.CREDENTIALS_MISSING,
            )


    async def test_graceful_degradation_on_timeout(self):
        """Databases that time out are recorded as unavailable."""
        available = {"life-sciences-genomics"}
        search = CrossDatabaseSearch(available, timeout=0.1)

        async def slow_query(query: str):
            await asyncio.sleep(5)
            return []

        search.register_query_fn("NCBI Gene", "life-sciences-genomics", slow_query)

        result = await search.search("BRCA1", SearchType.GENE)

        timeout_dbs = [
            u for u in result.unavailable_databases
            if u.reason == UnavailableReason.TIMEOUT
        ]
        assert len(timeout_dbs) >= 1

    async def test_graceful_degradation_on_api_error(self):
        """Databases that raise errors are recorded as unavailable."""
        available = {"life-sciences-genomics"}
        search = CrossDatabaseSearch(available, timeout=5.0)

        async def failing_query(query: str):
            raise RuntimeError("API connection failed")

        search.register_query_fn("NCBI Gene", "life-sciences-genomics", failing_query)

        result = await search.search("BRCA1", SearchType.GENE)

        error_dbs = [
            u for u in result.unavailable_databases
            if u.reason == UnavailableReason.API_ERROR
        ]
        assert len(error_dbs) >= 1

    async def test_partial_success(self):
        """Some databases succeed while others fail — results from
        successful ones are still returned."""
        available = {
            "life-sciences-genomics",
            "life-sciences-proteomics",
        }
        search = CrossDatabaseSearch(available, timeout=5.0)

        async def good_query(query: str):
            return [{"gene": query}]

        async def bad_query(query: str):
            raise RuntimeError("fail")

        search.register_query_fn("NCBI Gene", "life-sciences-genomics", good_query)
        search.register_query_fn("UniProt", "life-sciences-proteomics", bad_query)

        result = await search.search("TP53", SearchType.GENE)

        # NCBI Gene should succeed
        success_dbs = {r.database for r in result.results}
        assert "NCBI Gene" in success_dbs

        # UniProt should be in unavailable
        unavail_dbs = {u.database for u in result.unavailable_databases if u.reason == UnavailableReason.API_ERROR}
        assert "UniProt" in unavail_dbs

    async def test_no_servers_installed(self):
        """When no servers are installed, all databases are unavailable."""
        search = CrossDatabaseSearch(set(), timeout=5.0)
        result = await search.search("BRCA1", SearchType.GENE)

        assert len(result.results) == 0
        assert len(result.unavailable_databases) > 0
        for u in result.unavailable_databases:
            assert u.reason == UnavailableReason.NOT_INSTALLED
