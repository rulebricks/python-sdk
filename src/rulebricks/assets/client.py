# This file was auto-generated by Fern from our API Definition.

from ..core.client_wrapper import SyncClientWrapper
from .rules.client import RulesClient
from .flows.client import FlowsClient
from .folders.client import FoldersClient
import typing
from ..core.request_options import RequestOptions
from ..types.usage_statistics import UsageStatistics
from ..core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ..core.api_error import ApiError
from ..core.client_wrapper import AsyncClientWrapper
from .rules.client import AsyncRulesClient
from .flows.client import AsyncFlowsClient
from .folders.client import AsyncFoldersClient


class AssetsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper
        self.rules = RulesClient(client_wrapper=self._client_wrapper)
        self.flows = FlowsClient(client_wrapper=self._client_wrapper)
        self.folders = FoldersClient(client_wrapper=self._client_wrapper)

    def get_usage(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> UsageStatistics:
        """
        Get the rule execution usage of your organization.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        UsageStatistics
            Success

        Examples
        --------
        from rulebricks import Rulebricks

        client = Rulebricks(
            api_key="YOUR_API_KEY",
        )
        client.assets.get_usage()
        """
        _response = self._client_wrapper.httpx_client.request(
            "admin/usage",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    UsageStatistics,
                    parse_obj_as(
                        type_=UsageStatistics,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncAssetsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper
        self.rules = AsyncRulesClient(client_wrapper=self._client_wrapper)
        self.flows = AsyncFlowsClient(client_wrapper=self._client_wrapper)
        self.folders = AsyncFoldersClient(client_wrapper=self._client_wrapper)

    async def get_usage(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> UsageStatistics:
        """
        Get the rule execution usage of your organization.

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        UsageStatistics
            Success

        Examples
        --------
        import asyncio

        from rulebricks import AsyncRulebricks

        client = AsyncRulebricks(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.assets.get_usage()


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "admin/usage",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    UsageStatistics,
                    parse_obj_as(
                        type_=UsageStatistics,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
