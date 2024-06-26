# This file was auto-generated by Fern from our API Definition.

import typing

import httpx

from .core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from .resources.flows.client import AsyncFlowsClient, FlowsClient
from .resources.rules.client import AsyncRulesClient, RulesClient


class RulebricksApi:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: typing.Optional[float] = 60,
        httpx_client: typing.Optional[httpx.Client] = None
    ):
        self._client_wrapper = SyncClientWrapper(
            base_url=base_url,
            api_key=api_key,
            httpx_client=httpx.Client(timeout=timeout) if httpx_client is None else httpx_client,
        )
        self.rules = RulesClient(client_wrapper=self._client_wrapper)
        self.flows = FlowsClient(client_wrapper=self._client_wrapper)


class AsyncRulebricksApi:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: typing.Optional[float] = 60,
        httpx_client: typing.Optional[httpx.AsyncClient] = None
    ):
        self._client_wrapper = AsyncClientWrapper(
            base_url=base_url,
            api_key=api_key,
            httpx_client=httpx.AsyncClient(timeout=timeout) if httpx_client is None else httpx_client,
        )
        self.rules = AsyncRulesClient(client_wrapper=self._client_wrapper)
        self.flows = AsyncFlowsClient(client_wrapper=self._client_wrapper)
