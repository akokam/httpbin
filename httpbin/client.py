import httpx
from pydantic import BaseModel, BaseSettings, HttpUrl, ValidationError


# Define custom exceptions
# Purpose: Easy to catch by log management tools like Graylog
class ClientError(Exception):
    """Base error for all client errors"""


class NetworkError(ClientError):
    """Raised when request failed due to networking"""


class StatusError(ClientError):
    """Raised when request failed due to bad status"""


class ResponseError(ClientError):
    """Raised when request failed due to bad response"""


# Define models
# Purpose: Models are used to validate incoming/outgoing data
class GetResponse(BaseModel):
    origin: str


# Define a configuration for the client
# Purpose: Configs help switching the environments and come in handy for testing
class Config(BaseSettings):
    """Config for Client"""

    class Config:
        env_prefix = "OSRM_"

    base_url: HttpUrl = "https://httpbin.org"


# Define the client
# Purpose: Client does the call & all validation
class Client:
    def __init__(self, config: Config) -> None:
        self._http = httpx.Client(base_url=config.base_url)

    def get(self) -> GetResponse:
        """Get data from service"""

        # Make the call and catch potential networking errors
        try:
            response = self._http.get(url="/get")
        except (TimeoutError, ConnectionError) as e:
            raise NetworkError(e)

        # Validate the response for status
        try:
            response.raise_for_status()
        except httpx.HTTPError as e:
            StatusError(e)

        # Validate response data with model & return
        try:
            return GetResponse(**response.json())
        except ValidationError as e:
            raise ResponseError(e)
