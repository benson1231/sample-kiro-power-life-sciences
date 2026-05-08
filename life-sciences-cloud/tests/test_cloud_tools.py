"""Unit tests for life-sciences-cloud MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import AuthenticationError


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-cloud")
    yield srv
    await srv.cleanup()


class TestAWSBatchSubmit:
    @respx.mock
    async def test_aws_batch_submit(self, server: BaseLifeSciencesServer):
        from life_sciences_cloud.clients import aws_batch_client

        respx.post("https://batch.us-east-1.amazonaws.com/v1/submitjob").respond(
            200, json={"jobId": "job-123", "jobName": "test-job"},
        )
        result = await aws_batch_client.submit(
            server, "my-job-def", "my-queue", {"input": "s3://bucket/data"},
        )
        assert result["jobId"] == "job-123"


class TestAWSBatchStatus:
    @respx.mock
    async def test_aws_batch_status(self, server: BaseLifeSciencesServer):
        from life_sciences_cloud.clients import aws_batch_client

        respx.post("https://batch.us-east-1.amazonaws.com/v1/describejobs").respond(
            200, json={"jobs": [{"jobId": "job-123", "status": "SUCCEEDED"}]},
        )
        result = await aws_batch_client.status(server, "job-123")
        assert result["jobs"][0]["status"] == "SUCCEEDED"


class TestTerraWorkspaces:
    async def test_terra_requires_auth(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_cloud.clients import terra_client

        monkeypatch.delenv("TERRA_TOKEN", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await terra_client.workspaces(server)
        assert "TERRA_TOKEN" in exc_info.value.message

    @respx.mock
    async def test_terra_workspaces_with_token(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_cloud.clients import terra_client

        monkeypatch.setenv("TERRA_TOKEN", "test-token")
        respx.get("https://api.firecloud.org/api/workspaces").respond(
            200, json=[{"workspace": {"name": "my-workspace"}}],
        )
        result = await terra_client.workspaces(server)
        assert isinstance(result, list)


class TestGalaxyTools:
    @respx.mock
    async def test_galaxy_tools(self, server: BaseLifeSciencesServer):
        from life_sciences_cloud.clients import galaxy_client

        respx.get("https://usegalaxy.org/api/tools").respond(
            200, json=[{"id": "bwa", "name": "BWA"}],
        )
        result = await galaxy_client.tools(server)
        assert isinstance(result, list)


class TestGalaxySubmit:
    @respx.mock
    async def test_galaxy_submit(self, server: BaseLifeSciencesServer):
        from life_sciences_cloud.clients import galaxy_client

        respx.post("https://usegalaxy.org/api/tools").respond(
            200, json={"jobs": [{"id": "j1"}]},
        )
        result = await galaxy_client.submit(
            server, "https://usegalaxy.org", "bwa", {"input1": "data"},
        )
        assert "jobs" in result
