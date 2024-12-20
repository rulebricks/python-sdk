# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.jsonable_encoder import jsonable_encoder
from ...errors.bad_request_error import BadRequestError
from ...errors.internal_server_error import InternalServerError

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class FlowsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def execute(self, slug: str, *, request: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        Execute a flow by its slug.

        Parameters:
            - slug: str. The unique identifier for the flow.

            - request: typing.Dict[str, typing.Any].
        ---
        from rulebricks.client import RulebricksApi

        client = RulebricksApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        client.flows.execute(
            slug="slug",
            request={"name": "John Doe", "age": 30, "email": "jdoe@acme.co"},
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/v1/flows/{slug}"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Dict[str, typing.Any], _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncFlowsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def execute(self, slug: str, *, request: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        Execute a flow by its slug.

        Parameters:
            - slug: str. The unique identifier for the flow.

            - request: typing.Dict[str, typing.Any].
        ---
        from rulebricks.client import AsyncRulebricksApi

        client = AsyncRulebricksApi(
            api_key="YOUR_API_KEY",
            base_url="https://yourhost.com/path/to/api",
        )
        await client.flows.execute(
            slug="slug",
            request={"name": "John Doe", "age": 30, "email": "jdoe@acme.co"},
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/v1/flows/{slug}"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Dict[str, typing.Any], _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
