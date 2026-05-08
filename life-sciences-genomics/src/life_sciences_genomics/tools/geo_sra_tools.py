"""GEO and SRA tools for the genomics MCP server.

Tools
-----
- ``geo_search`` — Search GEO datasets by keyword.
- ``geo_get_dataset`` — Get a GEO dataset by accession.
- ``sra_search`` — Search SRA runs by keyword or BioProject.

Tool registration is handled centrally in ``server.py``.
Client logic lives in ``clients/geo_sra_client.py``.
"""
