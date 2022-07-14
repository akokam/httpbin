import httpx
import ipaddress
from pydantic import BaseModel, BaseSettings, ValidationError


class ClientError(Exception):
    """Base exception for httpbin client errors

    This exception shall be the base exception for all errors occuring in this client.

    ## Explanation
    Having a base error makes it easy to filter in log management tools like Graylog or
    catch exceptions more broadly.
    If you want to handle errors specificly, use the exceptions based on this one
    (e.g. retry strategies).
    """


class NetworkError(ClientError):
    """Networking exception for httpbin client

    Raised when request failed due to networking.
    """


class StatusError(ClientError):
    """Bad status exception for httpbin client

    Raised when request failed due to bad status.
    """


class ResponseError(ClientError):
    """Bad response exception for httpbin client

    Raised when request failed due to bad response.
    """


class GetResponse(BaseModel):
    """Response model for /get requests (selection)

    ## Explanation
    As a good habit, this client validates all responses with according to defined
    models. It's a good strategy to only validate (and keep) only attributes which
    are going to be consumed.

    ## Example (this actual model)
    The return of httpbin.org/get looks like this:
    ```
    {
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
            "X-Amzn-Trace-Id": "Root=1-62a6f30f-2d2e73766ad7c838411b3e04"
        },
        "origin": "194.39.218.10",
        "url": "https://httpbin.org/get"
    }
    ```
    But we only want to validate and keep `origin`.
    """

    origin: ipaddress.IPv4Address


# Define a configuration for the client
# Purpose: Configs help switching the environments (e.g. testing)
class Config(BaseSettings):
    """Config for httpbin client

    ## Explanation
    Configs are a good practice to set up clients. It allows us to quickly change
    attributes (e.g., for testing).

    The attributes of a config can have default values; like here. If a config
    attribute has no default, `BaseSettings` will search for it in the environment
    variables or in a `.env` file in the folder (see `Config` sub-class docstring).
    """

    class Config:
        """Settings for httpbin config

        ## Explanation
        `env_prefix` prefixes all attributes with it's value. We've got two options
        to overwrite `base_url`:
        1) Set the environment variable `HTTPBIN_BASE_URL=https:some-other.url`
        2) Add `HTTPBIN_BASE_URL=https://some-other.url` in a local `.env` file
        """

        env_prefix = "HTTPBIN_"

    base_url: str = "https://httpbin.org"


class Client:
    """Client for httpbin(.org)

    ## Background
    The client's responsibility is to make the calls, then report the error or return
    the validated response. Incoming and outgoing data is always validated with a model
    approach using pydantic's `BaseModel` (see `GetResponse` model).
    """

    def __init__(self, config: Config) -> None:
        self._http = httpx.Client(base_url=config.base_url)

    def get(self) -> GetResponse:
        """Get data from httpbin.org/get"""

        # Make the call and catch potential networking errors
        try:
            response = self._http.get(url="/get")
        except (TimeoutError, ConnectionError) as e:
            raise NetworkError(e)

        # Validate the response for status
        try:
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise StatusError(e)

        # Validate response data with model & return
        try:
            return GetResponse(**response.json())
        except ValidationError as e:
            raise ResponseError(e)
