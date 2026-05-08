"""Unit tests for life-sciences-pipelines MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-pipelines")
    yield srv
    await srv.cleanup()


class TestNfcoreList:
    @respx.mock
    async def test_nfcore_list(self, server: BaseLifeSciencesServer):
        from life_sciences_pipelines.clients import nfcore_client

        respx.get("https://nf-co.re/pipelines.json").respond(
            200,
            json={"remote_workflows": [{"name": "rnaseq"}, {"name": "sarek"}]},
        )
        result = await nfcore_client.list_pipelines(server)
        assert result["count"] == 2
        assert result["pipelines"][0]["name"] == "rnaseq"


class TestNfcorePipeline:
    @respx.mock
    async def test_nfcore_pipeline(self, server: BaseLifeSciencesServer):
        from life_sciences_pipelines.clients import nfcore_client

        respx.get("https://nf-co.re/pipelines.json").respond(
            200,
            json={"remote_workflows": [{"name": "rnaseq", "description": "RNA-Seq"}]},
        )
        result = await nfcore_client.get_pipeline(server, "rnaseq")
        assert result["name"] == "rnaseq"


class TestWDLList:
    async def test_wdl_list(self, server: BaseLifeSciencesServer):
        from life_sciences_pipelines.clients import wdl_client

        result = await wdl_client.list_pipelines(server)
        assert result["count"] >= 1
        assert all(p["language"] == "WDL" for p in result["pipelines"])


class TestGitHubPipelines:
    @respx.mock
    async def test_github_pipelines(self, server: BaseLifeSciencesServer):
        from life_sciences_pipelines.clients import github_client

        respx.get("https://api.github.com/search/repositories").respond(
            200,
            json={
                "total_count": 1,
                "items": [
                    {
                        "full_name": "nf-core/rnaseq",
                        "description": "RNA-Seq pipeline",
                        "stargazers_count": 500,
                        "html_url": "https://github.com/nf-core/rnaseq",
                        "language": "Nextflow",
                    }
                ],
            },
        )
        result = await github_client.search_pipelines(server, "rnaseq")
        assert result["total_count"] == 1
        assert result["pipelines"][0]["name"] == "nf-core/rnaseq"


class TestPipelineHealthOmicsImport:
    async def test_healthomics_import(self, server: BaseLifeSciencesServer):
        from life_sciences_pipelines.clients import github_client

        result = await github_client.healthomics_import(
            server, "nf-core/rnaseq", "nextflow",
        )
        assert result["workflow_language"] == "NEXTFLOW"
        assert "instructions" in result
        assert "step_1" in result["instructions"]
