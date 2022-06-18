from typing import Generator
import pytest
import respx
import pytest_mock
import httpx


import httpbin


@pytest.fixture
def mocked_api() -> Generator:
    """Provide a mocked API to be used in tests"""
    with respx.mock(base_url="https://test.url", assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def candidate() -> httpbin.Client:
    """Provide a httpbin client for testing"""
    cfg = httpbin.Config(base_url="https://test.url")
    return httpbin.Client(cfg)


class TestClient:
    def test_get(
        self,
        candidate: httpbin.Client,
        mocked_api: respx.MockRouter,
    ) -> None:
        """SCENARIO: Request to /get (happy path)
        TEST: Data is received, parsed, validateds and returned
        """
        get_route = mocked_api.get("/get", name="get")
        get_route.return_value = httpx.Response(
            200,
            json={
                "args": {},
                "headers": {
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "de-DE",
                    "Dnt": "1",
                    "Host": "httpbin.org",
                    "Referer": "https://httpbin.org/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla...1.0",
                    "X-Amzn-Trace-Id": "Root=1...3e04",
                },
                "origin": "194.39.218.10",
                "url": "https://httpbin.org/get",
            },
        )

        candidate.get()

        assert mocked_api["get"].called

    @pytest.mark.parametrize(
        "error",
        [
            pytest.param(TimeoutError, id="Timeout"),
            pytest.param(ConnectionError, id="Connection"),
        ],
    )
    def test_get__bad_network(
        self,
        candidate: httpbin.Client,
        mocker: pytest_mock.MockerFixture,
        error: OSError,
    ) -> None:
        """SCENARIO: Request to /get (failed due to network issues)
        TEST: Exception is raised
        """
        mocker.patch.object(httpx.Client, "get", side_effect=error)

        with pytest.raises(httpbin.client.NetworkError):
            candidate.get()

    @pytest.mark.parametrize(
        "status_code",
        [
            pytest.param(400, id="Client errors"),
            pytest.param(500, id="Server errors"),
        ],
    )
    def test_get__bad_status(
        self,
        candidate: httpbin.Client,
        mocked_api: respx.MockRouter,
        status_code: int,
    ) -> None:
        """SCENARIO: Request to /get (failed due to bad status)
        TEST: Exception is raised
        """
        get_route = mocked_api.get("/get", name="get")
        get_route.return_value = httpx.Response(status_code)

        with pytest.raises(httpbin.client.StatusError):
            candidate.get()

    def test_get__bad_response(
        self,
        candidate: httpbin.Client,
        mocked_api: respx.MockRouter,
    ) -> None:
        """SCENARIO: Request to /get (failed due to bad response)
        TEST: Exception is raised
        """
        get_route = mocked_api.get("/get", name="get")
        get_route.return_value = httpx.Response(200, json={})

        with pytest.raises(httpbin.client.ResponseError):
            candidate.get()
