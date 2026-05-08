"""Unit tests for BaseLifeSciencesServer and custom exception classes.

Uses ``respx`` to mock httpx responses.
"""

from __future__ import annotations

import pytest
import httpx
import respx

from life_sciences_common.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
)
from life_sciences_common.server import BaseLifeSciencesServer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def base_url() -> str:
    return "https://api.example.com"


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-server")
    yield srv
    await srv.cleanup()


# ---------------------------------------------------------------------------
# Exception class tests
# ---------------------------------------------------------------------------

class TestExceptionClasses:
    def test_api_error_with_status(self):
        err = APIError(service="NCBI", status_code=400, message="Bad request")
        assert err.service == "NCBI"
        assert err.status_code == 400
        assert err.message == "Bad request"
        assert "[NCBI 400]" in str(err)

    def test_api_error_without_status(self):
        err = APIError(service="NCBI", message="Network issue")
        assert err.status_code is None
        assert "[NCBI]" in str(err)

    def test_rate_limit_error_defaults(self):
        err = RateLimitError(service="UniProt")
        assert err.status_code == 429
        assert "Rate limit exceeded" in err.message
        assert "UniProt" in err.message

    def test_rate_limit_error_custom_message(self):
        err = RateLimitError(service="UniProt", message="custom msg")
        assert err.message == "custom msg"

    def test_authentication_error_with_url(self):
        err = AuthenticationError(
            service="COSMIC",
            obtain_url="https://cancer.sanger.ac.uk/cosmic/register",
        )
        assert err.status_code == 401
        assert "COSMIC" in err.message
        assert "https://cancer.sanger.ac.uk/cosmic/register" in err.message
        assert err.obtain_url == "https://cancer.sanger.ac.uk/cosmic/register"

    def test_authentication_error_403(self):
        err = AuthenticationError(service="OMIM", status_code=403)
        assert err.status_code == 403

    def test_not_found_error_with_query(self):
        err = NotFoundError(service="PDB", query="BRCA1")
        assert err.status_code == 404
        assert "PDB" in err.message
        assert "BRCA1" in err.message

    def test_not_found_error_without_query(self):
        err = NotFoundError(service="PDB")
        assert "No results found in PDB" in err.message

    def test_service_unavailable_error(self):
        err = ServiceUnavailableError(service="Ensembl", status_code=503)
        assert err.status_code == 503
        assert "Ensembl" in err.message

    def test_service_unavailable_no_status(self):
        err = ServiceUnavailableError(service="Ensembl")
        assert err.status_code is None

    def test_inheritance_chain(self):
        assert issubclass(RateLimitError, APIError)
        assert issubclass(AuthenticationError, APIError)
        assert issubclass(NotFoundError, APIError)
        assert issubclass(ServiceUnavailableError, APIError)
        assert issubclass(APIError, Exception)


# ---------------------------------------------------------------------------
# BaseLifeSciencesServer initialisation
# ---------------------------------------------------------------------------

class TestServerInit:
    async def test_creates_mcp_server(self, server: BaseLifeSciencesServer):
        assert server.server.name == "test-server"

    async def test_creates_http_client(self, server: BaseLifeSciencesServer):
        assert isinstance(server.http_client, httpx.AsyncClient)

    async def test_cleanup_closes_client(self):
        srv = BaseLifeSciencesServer("tmp")
        assert not srv.http_client.is_closed
        await srv.cleanup()
        assert srv.http_client.is_closed


# ---------------------------------------------------------------------------
# _request_with_retry – rate-limit (429) handling
# ---------------------------------------------------------------------------

class TestRateLimitRetry:
    @respx.mock
    async def test_retries_on_429_then_succeeds(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        route = respx.get(url).side_effect = [
            httpx.Response(429),
            httpx.Response(200, json={"ok": True}),
        ]
        respx.get(url).side_effect = [
            httpx.Response(429),
            httpx.Response(200, json={"ok": True}),
        ]
        resp = await server._request_with_retry("GET", url, max_retries=3)
        assert resp.status_code == 200

    @respx.mock
    async def test_raises_rate_limit_error_after_exhaustion(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = [
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),  # attempt 0,1,2,3
        ]
        with pytest.raises(RateLimitError):
            await server._request_with_retry("GET", url, max_retries=3)

    @respx.mock
    async def test_respects_retry_after_header(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = [
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"ok": True}),
        ]
        resp = await server._request_with_retry("GET", url, max_retries=3)
        assert resp.status_code == 200

    @respx.mock
    async def test_invalid_retry_after_falls_back_to_exponential(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = [
            httpx.Response(429, headers={"Retry-After": "not-a-number"}),
            httpx.Response(200, json={"ok": True}),
        ]
        resp = await server._request_with_retry("GET", url, max_retries=3)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# _request_with_retry – server error (5xx) handling
# ---------------------------------------------------------------------------

class TestServerErrorRetry:
    @respx.mock
    async def test_retries_once_on_5xx_then_succeeds(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = [
            httpx.Response(503),
            httpx.Response(200, json={"ok": True}),
        ]
        resp = await server._request_with_retry("GET", url)
        assert resp.status_code == 200

    @respx.mock
    async def test_returns_5xx_after_single_retry(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = [
            httpx.Response(500),
            httpx.Response(502),
        ]
        resp = await server._request_with_retry("GET", url)
        # After one retry the second 5xx is returned (not retried again)
        assert resp.status_code == 502


# ---------------------------------------------------------------------------
# _request_with_retry – timeout handling
# ---------------------------------------------------------------------------

class TestTimeoutRetry:
    @respx.mock
    async def test_retries_once_on_timeout_then_succeeds(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = [
            httpx.TimeoutException("read timed out"),
            httpx.Response(200, json={"ok": True}),
        ]
        resp = await server._request_with_retry("GET", url)
        assert resp.status_code == 200

    @respx.mock
    async def test_raises_timeout_after_second_failure(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = [
            httpx.TimeoutException("read timed out"),
            httpx.TimeoutException("read timed out again"),
        ]
        with pytest.raises(httpx.TimeoutException):
            await server._request_with_retry("GET", url)


# ---------------------------------------------------------------------------
# _request_with_retry – connection error (unreachable)
# ---------------------------------------------------------------------------

class TestConnectionError:
    @respx.mock
    async def test_raises_immediately_on_connect_error(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).side_effect = httpx.ConnectError("Connection refused")
        with pytest.raises(httpx.ConnectError):
            await server._request_with_retry("GET", url)


# ---------------------------------------------------------------------------
# _request_with_retry – successful responses
# ---------------------------------------------------------------------------

class TestSuccessfulRequests:
    @respx.mock
    async def test_returns_200_immediately(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/data"
        respx.get(url).respond(200, json={"result": "ok"})
        resp = await server._request_with_retry("GET", url)
        assert resp.status_code == 200
        assert resp.json() == {"result": "ok"}

    @respx.mock
    async def test_post_request(
        self, server: BaseLifeSciencesServer, base_url: str
    ):
        url = f"{base_url}/submit"
        respx.post(url).respond(201, json={"id": 1})
        resp = await server._request_with_retry("POST", url, json={"q": "test"})
        assert resp.status_code == 201


# ---------------------------------------------------------------------------
# _handle_api_error
# ---------------------------------------------------------------------------

class TestHandleApiError:
    async def test_2xx_does_not_raise(self, server: BaseLifeSciencesServer):
        response = httpx.Response(200)
        await server._handle_api_error(response, "TestService")

    async def test_401_raises_authentication_error(self, server: BaseLifeSciencesServer):
        response = httpx.Response(401, text="Unauthorized")
        with pytest.raises(AuthenticationError) as exc_info:
            await server._handle_api_error(
                response, "COSMIC", obtain_url="https://example.com/register"
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.obtain_url == "https://example.com/register"

    async def test_403_raises_authentication_error(self, server: BaseLifeSciencesServer):
        response = httpx.Response(403, text="Forbidden")
        with pytest.raises(AuthenticationError) as exc_info:
            await server._handle_api_error(response, "OMIM")
        assert exc_info.value.status_code == 403

    async def test_404_raises_not_found_error(self, server: BaseLifeSciencesServer):
        response = httpx.Response(404, text="Not Found")
        with pytest.raises(NotFoundError) as exc_info:
            await server._handle_api_error(response, "PDB", query="BRCA1")
        assert exc_info.value.query == "BRCA1"

    async def test_500_raises_service_unavailable(self, server: BaseLifeSciencesServer):
        response = httpx.Response(500, text="Internal Server Error")
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await server._handle_api_error(response, "Ensembl")
        assert exc_info.value.status_code == 500

    async def test_502_raises_service_unavailable(self, server: BaseLifeSciencesServer):
        response = httpx.Response(502, text="Bad Gateway")
        with pytest.raises(ServiceUnavailableError):
            await server._handle_api_error(response, "Ensembl")

    async def test_generic_4xx_raises_api_error(self, server: BaseLifeSciencesServer):
        response = httpx.Response(422, text="Unprocessable Entity")
        with pytest.raises(APIError) as exc_info:
            await server._handle_api_error(response, "UniProt")
        assert exc_info.value.status_code == 422
        assert "422" in exc_info.value.message
