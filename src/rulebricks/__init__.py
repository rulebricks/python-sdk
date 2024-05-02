from typing import Optional
from .client import RulebricksApi, AsyncRulebricksApi
from .errors import BadRequestError, InternalServerError
from .resources.rules.client import RulesClient, AsyncRulesClient
from .resources.flows.client import FlowsClient, AsyncFlowsClient

class Config:
    api_key: Optional[str] = None
    base_url: str = "https://rulebricks.com"
    timeout: float = 60

def set_api_key(api_key: str) -> None:
    Config.api_key = api_key
    APIManager.reset_instances()

def set_instance_url(base_url: str) -> None:
    Config.base_url = base_url
    APIManager.reset_instances()

def set_timeout(timeout: float) -> None:
    Config.timeout = timeout
    APIManager.reset_instances()

class APIManager:
    _instance: Optional[RulebricksApi] = None
    _async_instance: Optional[AsyncRulebricksApi] = None

    @staticmethod
    def reset_instances():
        APIManager._instance = None
        APIManager._async_instance = None

    @staticmethod
    def get_api() -> RulebricksApi:
        if APIManager._instance is None:
            if Config.api_key is None:
                raise ValueError("API key not set. Please set the API key first.")
            APIManager._instance = RulebricksApi(
                base_url=Config.base_url,
                api_key=Config.api_key,
                timeout=Config.timeout
            )
        assert APIManager._instance is not None, "Instance of AsyncRulebricksApi should not be None"
        return APIManager._instance

    @staticmethod
    async def get_async_api() -> AsyncRulebricksApi:
        if APIManager._async_instance is None:
            if Config.api_key is None:
                raise ValueError("API key not set. Please set the API key first.")
            APIManager._async_instance = AsyncRulebricksApi(
                base_url=Config.base_url,
                api_key=Config.api_key,
                timeout=Config.timeout
            )
        assert APIManager._async_instance is not None, "Instance of AsyncRulebricksApi should not be None"
        return APIManager._async_instance

# Synchronous API
rules = APIManager.get_api().rules
flows = APIManager.get_api().flows

# Asynchronous API
class AsyncAPI:
    @property
    async def rules(self) -> AsyncRulesClient:
        return (await APIManager.get_async_api()).rules

    @property
    async def flows(self) -> AsyncFlowsClient:
        return (await APIManager.get_async_api()).flows

async_api = AsyncAPI()

__all__ = [
    "BadRequestError",
    "InternalServerError",
    "ListResponseItem",
    "ListResponseItemRequestSchemaItem",
    "ListResponseItemResponseSchemaItem",
    "UsageResponse",
    "async_api",
    "set_api_key",
    "set_instance_url",
    "set_timeout",
    "rules",
    "flows",
]
