from typing import Optional
from .client import RulebricksApi, AsyncRulebricksApi
from .errors import BadRequestError, InternalServerError
from .resources import (
    ListResponseItem,
    ListResponseItemRequestSchemaItem,
    ListResponseItemResponseSchemaItem,
    UsageResponse
)

class Config:
    api_key: Optional[str] = None
    base_url: str = "https://rulebricks.com"

class APIManager:
    _instance: Optional[RulebricksApi] = None
    _async_instance: Optional[AsyncRulebricksApi] = None

    @staticmethod
    def get_api() -> RulebricksApi:
        if APIManager._instance is None:
            if Config.api_key is None:
                raise ValueError("API key not set. Please set the API key first.")
            APIManager._instance = RulebricksApi(base_url=Config.base_url, api_key=Config.api_key)
        return APIManager._instance

    @staticmethod
    async def get_async_api() -> AsyncRulebricksApi:
        if APIManager._async_instance is None:
            if Config.api_key is None:
                raise ValueError("API key not set. Please set the API key first.")
            APIManager._async_instance = AsyncRulebricksApi(base_url=Config.base_url, api_key=Config.api_key)
        return APIManager._async_instance

def set_api_key(api_key: str) -> None:
    Config.api_key = api_key
    APIManager._instance = None
    APIManager._async_instance = None

def set_instance_url(base_url: str) -> None:
    Config.base_url = base_url
    APIManager._instance = None
    APIManager._async_instance = None

class Flows:
    def __getattr__(self, name):
        api = APIManager.get_api()
        return getattr(api.flows, name)

class Rules:
    def __getattr__(self, name):
        api = APIManager.get_api()
        return getattr(api.rules, name)

class AsyncAPI:
    def __getattr__(self, name):
        async def wrapper(*args, **kwargs):
            api = await APIManager.get_async_api()
            return await getattr(api, name)(*args, **kwargs)
        return wrapper

flows = Flows()
rules = Rules()
async_api = AsyncAPI()

__all__ = [
    "BadRequestError",
    "InternalServerError",
    "ListResponseItem",
    "ListResponseItemRequestSchemaItem",
    "ListResponseItemResponseSchemaItem",
    "UsageResponse",
    "flows",
    "rules",
    "async_api",
    "set_api_key",
    "set_instance_url",
]