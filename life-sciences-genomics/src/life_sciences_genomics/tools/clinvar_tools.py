"""ClinVar tools for the genomics MCP server.

Tools
-----
- ``clinvar_search`` — Search ClinVar by rsID, HGVS, or gene name.
- ``clinvar_get_variation`` — Get a full variation record by ID.

Tool registration is handled centrally in ``server.py``.
Client logic lives in ``clients/clinvar_client.py``.
"""
