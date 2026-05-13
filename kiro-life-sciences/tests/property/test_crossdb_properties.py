"""Property-based tests for the cross-database search skill.

Uses Hypothesis to verify search mapping and graceful degradation
properties.  Each test runs a minimum of 100 iterations.
"""

from __future__ import annotations

import asyncio

from hypothesis import given, settings, strategies as st, assume

from kiro_life_sciences.skills.cross_database_search import (
    CrossDatabaseSearch,
    SEARCH_TYPE_DATABASE_MAP,
    SearchType,
    UnavailableReason,
)


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

_search_type_st = st.sampled_from(list(SearchType))

_query_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_ "),
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip() != "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_async(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ===========================================================================
# Property 17: Cross-Database Search Queries Correct Databases (Task 21.2)
# ===========================================================================
# Feature: kiro-life-sciences, Property 17: Cross-Database Search Mapping


@st.composite
def search_with_all_servers_st(draw):
    """Generate a search type with all mapped servers available and
    query functions registered that return mock results."""
    search_type = draw(_search_type_st)
    query = draw(_query_st)
    databases = SEARCH_TYPE_DATABASE_MAP[search_type]

    # All servers are available
    all_servers = {server for _, server in databases}

    return search_type, query, all_servers, databases


class TestCrossDatabaseSearchMapping:
    """For any search type, the search queries exactly the databases in the
    mapping, results grouped by database with no duplicates.

    **Validates: Requirements 54.2, 54.3, 54.4, 54.5, 54.6, 54.7**
    """

    @given(data=search_with_all_servers_st())
    @settings(max_examples=100)
    def test_queries_correct_databases(self, data):
        search_type, query, all_servers, expected_databases = data

        search = CrossDatabaseSearch(
            available_servers=all_servers,
            timeout=5.0,
        )

        # Register mock query functions for all databases
        for db_name, server_name in expected_databases:
            async def mock_fn(q, _db=db_name):
                return [{"id": f"{_db}-result-1", "query": q}]
            search.register_query_fn(db_name, server_name, mock_fn)

        result = _run_async(search.search(query, search_type))

        # Results should be grouped by database
        result_databases = {r.database for r in result.results}
        expected_db_names = {db for db, _ in expected_databases}

        # All expected databases should have results
        assert result_databases == expected_db_names, (
            f"Expected databases {expected_db_names}, got {result_databases}"
        )

        # No database appears more than once in results
        db_names_list = [r.database for r in result.results]
        assert len(db_names_list) == len(set(db_names_list)), (
            "Duplicate database in results"
        )

        # No unavailable databases when all servers are available and registered
        assert len(result.unavailable_databases) == 0

        # Query and search type are preserved
        assert result.query == query
        assert result.search_type == search_type


# ===========================================================================
# Property 18: Cross-Database Search Graceful Degradation (Task 21.3)
# ===========================================================================
# Feature: kiro-life-sciences, Property 18: Cross-Database Graceful Degradation


@st.composite
def search_with_failures_st(draw):
    """Generate a search type with a random subset of servers failing."""
    search_type = draw(_search_type_st)
    query = draw(_query_st)
    databases = SEARCH_TYPE_DATABASE_MAP[search_type]
    assume(len(databases) >= 2)

    all_servers = {server for _, server in databases}

    # Randomly pick a subset of servers to be unavailable (not installed)
    unavailable_servers = draw(st.frozensets(
        st.sampled_from(sorted(all_servers)),
        min_size=1,
        max_size=max(1, len(all_servers) - 1),
    ))
    available_servers = all_servers - unavailable_servers

    return search_type, query, available_servers, unavailable_servers, databases


class TestCrossDatabaseGracefulDegradation:
    """When a subset of databases fail, results from successful ones are
    returned, and unavailable list contains exactly the failed ones.

    **Validates: Requirements 54.8**
    """

    @given(data=search_with_failures_st())
    @settings(max_examples=100)
    def test_graceful_degradation(self, data):
        search_type, query, available_servers, unavailable_servers, all_databases = data

        search = CrossDatabaseSearch(
            available_servers=available_servers,
            timeout=5.0,
        )

        # Register mock query functions only for available servers
        for db_name, server_name in all_databases:
            if server_name in available_servers:
                async def mock_fn(q, _db=db_name):
                    return [{"id": f"{_db}-result", "query": q}]
                search.register_query_fn(db_name, server_name, mock_fn)

        result = _run_async(search.search(query, search_type))

        # Databases on unavailable servers should be in unavailable list
        unavailable_db_names = {u.database for u in result.unavailable_databases}
        for db_name, server_name in all_databases:
            if server_name not in available_servers:
                assert db_name in unavailable_db_names, (
                    f"Database {db_name} on unavailable server {server_name} "
                    f"should be in unavailable list"
                )
                # Check reason is NOT_INSTALLED
                for u in result.unavailable_databases:
                    if u.database == db_name:
                        assert u.reason == UnavailableReason.NOT_INSTALLED

        # Databases on available servers should have results (since we registered fns)
        result_db_names = {r.database for r in result.results}
        for db_name, server_name in all_databases:
            if server_name in available_servers:
                assert db_name in result_db_names, (
                    f"Database {db_name} on available server {server_name} "
                    f"should have results"
                )

        # Results from successful databases are returned
        for r in result.results:
            assert r.result_count > 0
