"""NCBI Entrez tools for the genomics MCP server.

Provides search across NCBI databases, sequence fetching, and PubMed search.

Tools
-----
- ``ncbi_search`` — Search any NCBI database via Entrez esearch.
- ``ncbi_fetch_sequence`` — Fetch a nucleotide sequence by accession.
- ``ncbi_pubmed_search`` — Search PubMed and return article summaries.

Tool registration is handled centrally in ``server.py``.
Client logic lives in ``clients/ncbi_client.py``.
"""
