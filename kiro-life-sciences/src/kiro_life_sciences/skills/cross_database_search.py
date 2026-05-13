"""Cross-database search skill.

Orchestrates parallel queries across multiple installed MCP servers,
grouping results by database and gracefully handling failures.

Implements the Cross-Database Search Skill from the design document
(Components and Interfaces §7).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT_SECONDS: float = 10.0
"""Per-database query timeout in seconds."""


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SearchType(StrEnum):
    """Supported cross-database search types."""

    GENE = "gene"
    DRUG = "drug"
    PROTEIN = "protein"
    SPECIES = "species"
    METABOLITE = "metabolite"
    CELL_TYPE = "cell_type"


class UnavailableReason(StrEnum):
    """Reason codes for databases that could not be queried."""

    NOT_INSTALLED = "not_installed"
    CREDENTIALS_MISSING = "credentials_missing"
    API_ERROR = "api_error"
    TIMEOUT = "timeout"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DatabaseGroupResult:
    """Results from a single database within a cross-database search."""

    database: str
    mcp_server: str
    entries: list[Any] = field(default_factory=list)
    result_count: int = 0


@dataclass(frozen=True)
class UnavailableDatabase:
    """A database that could not be queried, with a reason code."""

    database: str
    reason: UnavailableReason


@dataclass(frozen=True)
class CrossDatabaseSearchResult:
    """Aggregated result of a cross-database search."""

    query: str
    search_type: str
    results: list[DatabaseGroupResult] = field(default_factory=list)
    unavailable_databases: list[UnavailableDatabase] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Search-type → database mapping
# ---------------------------------------------------------------------------

#: Maps each search type to a list of ``(database_name, mcp_server_name)``
#: tuples.  The MCP server name corresponds to the key used in ``mcp.json``.
SEARCH_TYPE_DATABASE_MAP: dict[str, list[tuple[str, str]]] = {
    SearchType.GENE: [
        ("NCBI Gene", "life-sciences-genomics"),
        ("UniProt", "life-sciences-proteomics"),
        ("Ensembl", "life-sciences-genomics"),
        ("ClinVar", "life-sciences-genomics"),
        ("OMIM", "life-sciences-clinical"),
        ("Gene Ontology", "life-sciences-ontologies"),
        ("KEGG", "life-sciences-pathways"),
        ("Reactome", "life-sciences-pathways"),
        ("Allen Brain Atlas", "life-sciences-neuroscience"),
        ("IEDB", "life-sciences-immunology"),
        ("CellxGene", "life-sciences-cellbiology"),
    ],
    SearchType.DRUG: [
        ("DrugBank", "life-sciences-clinical"),
        ("ChEMBL", "life-sciences-clinical"),
        ("PharmGKB", "life-sciences-clinical"),
        ("OpenTargets", "life-sciences-clinical"),
        ("PubChem", "life-sciences-cheminformatics"),
        ("HMDB", "life-sciences-metabolomics"),
        ("CARD", "life-sciences-microbiology"),
    ],
    SearchType.PROTEIN: [
        ("UniProt", "life-sciences-proteomics"),
        ("PDB", "life-sciences-structural"),
        ("AlphaFold DB", "life-sciences-structural"),
        ("InterPro", "life-sciences-proteomics"),
        ("STRING", "life-sciences-proteomics"),
        ("neXtProt", "life-sciences-proteomics"),
        ("ESM", "life-sciences-aiml"),
        ("abYsis", "life-sciences-immunology"),
    ],
    SearchType.SPECIES: [
        ("GBIF", "life-sciences-ecology"),
        ("IUCN Red List", "life-sciences-ecology"),
        ("BOLD", "life-sciences-ecology"),
        ("iNaturalist", "life-sciences-ecology"),
        ("NCBI Taxonomy", "life-sciences-genomics"),
        ("MGnify", "life-sciences-microbiology"),
    ],
    SearchType.METABOLITE: [
        ("HMDB", "life-sciences-metabolomics"),
        ("MetaboLights", "life-sciences-metabolomics"),
        ("METLIN", "life-sciences-metabolomics"),
        ("MassBank", "life-sciences-metabolomics"),
        ("PubChem", "life-sciences-cheminformatics"),
        ("KEGG", "life-sciences-pathways"),
    ],
    SearchType.CELL_TYPE: [
        ("CellxGene", "life-sciences-cellbiology"),
        ("Single Cell Expression Atlas", "life-sciences-cellbiology"),
        ("Cell Atlas", "life-sciences-cellbiology"),
        ("Allen Brain Atlas", "life-sciences-neuroscience"),
    ],
}


# ---------------------------------------------------------------------------
# Cross-database search implementation
# ---------------------------------------------------------------------------


class CrossDatabaseSearch:
    """Orchestrates parallel queries across multiple life-sciences databases.

    Parameters
    ----------
    available_servers:
        Set of MCP server names that are currently installed and reachable.
        Server names should match the keys used in ``mcp.json``
        (e.g. ``"life-sciences-genomics"``).
    timeout:
        Per-database query timeout in seconds.  Defaults to
        :data:`DEFAULT_TIMEOUT_SECONDS` (10 s).
    """

    def __init__(
        self,
        available_servers: set[str],
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._available_servers = set(available_servers)
        self._timeout = timeout
        # Registry of query functions keyed by (database, mcp_server).
        # Callers can register real query implementations via
        # ``register_query_fn``.
        self._query_fns: dict[tuple[str, str], Any] = {}

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def register_query_fn(
        self,
        database: str,
        mcp_server: str,
        fn: Any,
    ) -> None:
        """Register an async query function for a specific database.

        The function signature must be::

            async def fn(query: str) -> list[Any]

        It should raise :class:`Exception` on API errors so that the
        search can record the failure and continue.
        """
        self._query_fns[(database, mcp_server)] = fn

    @staticmethod
    def get_databases_for_search_type(search_type: str) -> list[tuple[str, str]]:
        """Return the ``(database, mcp_server)`` pairs for *search_type*.

        Raises :class:`ValueError` if *search_type* is not recognised.
        """
        mapping = SEARCH_TYPE_DATABASE_MAP.get(search_type)
        if mapping is None:
            valid = ", ".join(sorted(SEARCH_TYPE_DATABASE_MAP))
            raise ValueError(
                f"Unknown search type {search_type!r}. "
                f"Valid types: {valid}"
            )
        return list(mapping)

    # ------------------------------------------------------------------
    # Core search
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        search_type: str,
    ) -> CrossDatabaseSearchResult:
        """Execute a cross-database search.

        Queries all databases mapped to *search_type* in parallel.  Each
        database query is subject to the configured timeout.  Databases
        whose MCP server is not installed are recorded as unavailable
        with reason ``not_installed``.  Databases that time out are
        recorded with reason ``timeout``.  Databases that raise any
        other exception are recorded with reason ``api_error``.

        Returns a :class:`CrossDatabaseSearchResult` containing results
        from all successful databases and a list of unavailable ones.
        """
        databases = self.get_databases_for_search_type(search_type)

        results: list[DatabaseGroupResult] = []
        unavailable: list[UnavailableDatabase] = []

        # Partition databases into queryable and not-installed.
        queryable: list[tuple[str, str]] = []
        for db_name, server_name in databases:
            if server_name not in self._available_servers:
                unavailable.append(
                    UnavailableDatabase(
                        database=db_name,
                        reason=UnavailableReason.NOT_INSTALLED,
                    )
                )
            else:
                queryable.append((db_name, server_name))

        # Run all queryable databases in parallel.
        if queryable:
            tasks = [
                self._query_database(query, db_name, server_name)
                for db_name, server_name in queryable
            ]
            outcomes = await asyncio.gather(*tasks, return_exceptions=False)

            for outcome in outcomes:
                if isinstance(outcome, DatabaseGroupResult):
                    results.append(outcome)
                elif isinstance(outcome, UnavailableDatabase):
                    unavailable.append(outcome)

        return CrossDatabaseSearchResult(
            query=query,
            search_type=search_type,
            results=results,
            unavailable_databases=unavailable,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _query_database(
        self,
        query: str,
        database: str,
        mcp_server: str,
    ) -> DatabaseGroupResult | UnavailableDatabase:
        """Query a single database with timeout handling."""
        query_fn = self._query_fns.get((database, mcp_server))
        if query_fn is None:
            # No query function registered — treat as credentials missing
            # (the server is installed but we have no way to query this
            # specific database).
            return UnavailableDatabase(
                database=database,
                reason=UnavailableReason.CREDENTIALS_MISSING,
            )

        try:
            entries = await asyncio.wait_for(
                query_fn(query),
                timeout=self._timeout,
            )
            return DatabaseGroupResult(
                database=database,
                mcp_server=mcp_server,
                entries=list(entries) if entries else [],
                result_count=len(entries) if entries else 0,
            )
        except asyncio.TimeoutError:
            return UnavailableDatabase(
                database=database,
                reason=UnavailableReason.TIMEOUT,
            )
        except Exception:  # noqa: BLE001 — intentional broad catch
            return UnavailableDatabase(
                database=database,
                reason=UnavailableReason.API_ERROR,
            )
