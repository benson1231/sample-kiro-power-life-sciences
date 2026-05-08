"""Ensembl REST tools for the genomics MCP server.

Tools
-----
- ``ensembl_gene_lookup`` — Lookup a gene by symbol and species.
- ``ensembl_variants`` — Get variants in a genomic region.
- ``ensembl_sequence`` — Get nucleotide sequence for a region.

Tool registration is handled centrally in ``server.py``.
Client logic lives in ``clients/ensembl_client.py``.
"""
