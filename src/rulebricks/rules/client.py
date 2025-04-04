# This file was auto-generated by Fern from our API Definition.

import typing
from ..core.client_wrapper import SyncClientWrapper
from ..types.dynamic_request_payload import DynamicRequestPayload
from ..core.request_options import RequestOptions
from ..types.dynamic_response_payload import DynamicResponsePayload
from ..core.jsonable_encoder import jsonable_encoder
from ..core.pydantic_utilities import parse_obj_as
from ..errors.bad_request_error import BadRequestError
from ..errors.internal_server_error import InternalServerError
from json.decoder import JSONDecodeError
from ..core.api_error import ApiError
from ..types.bulk_rule_response_item import BulkRuleResponseItem
from ..types.parallel_solve_request import ParallelSolveRequest
from ..types.parallel_solve_response import ParallelSolveResponse
from ..core.serialization import convert_and_respect_annotation_metadata
from ..core.client_wrapper import AsyncClientWrapper

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class RulesClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def solve(
        self,
        slug: str,
        *,
        request: DynamicRequestPayload,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> DynamicResponsePayload:
        """
        Executes a single rule identified by a unique slug. The request and response formats are dynamic, dependent on the rule configuration.

        Parameters
        ----------
        slug : str
            The unique identifier for the resource.

        request : DynamicRequestPayload

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        DynamicResponsePayload
            Rule execution successful. The response structure depends on the rule configuration.

        Examples
        --------
        from rulebricks import Rulebricks

        client = Rulebricks(
            api_key="YOUR_API_KEY",
        )
        client.rules.solve(
            slug="slug",
            request={"name": "John Doe", "age": 30, "email": "jdoe@acme.co"},
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"solve/{jsonable_encoder(slug)}",
            method="POST",
            json=request,
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    DynamicResponsePayload,
                    parse_obj_as(
                        type_=DynamicResponsePayload,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 400:
                raise BadRequestError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 500:
                raise InternalServerError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def bulk_solve(
        self,
        slug: str,
        *,
        request: typing.Sequence[DynamicRequestPayload],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[BulkRuleResponseItem]:
        """
        Executes a particular rule against multiple request data payloads provided in a list.

        Parameters
        ----------
        slug : str
            The unique identifier for the resource.

        request : typing.Sequence[DynamicRequestPayload]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[BulkRuleResponseItem]
            Bulk rule execution successful. The response is an array of results, each dependent on the rule configuration.

        Examples
        --------
        from rulebricks import Rulebricks

        client = Rulebricks(
            api_key="YOUR_API_KEY",
        )
        client.rules.bulk_solve(
            slug="slug",
            request=[
                {"name": "John Doe", "age": 30, "email": "jdoe@acme.co"},
                {"name": "Jane Doe", "age": 28, "email": "jane@example.com"},
            ],
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"bulk-solve/{jsonable_encoder(slug)}",
            method="POST",
            json=request,
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[BulkRuleResponseItem],
                    parse_obj_as(
                        type_=typing.List[BulkRuleResponseItem],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 400:
                raise BadRequestError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 500:
                raise InternalServerError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def parallel_solve(
        self,
        *,
        request: ParallelSolveRequest,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ParallelSolveResponse:
        """
        Executes multiple rules or flows in parallel based on a provided mapping of rule/flow slugs to payloads.

        Parameters
        ----------
        request : ParallelSolveRequest

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ParallelSolveResponse
            Parallel execution successful. The response is an object mirroring the request structure, but providing each rule/flow's results instead.

        Examples
        --------
        from rulebricks import ParallelSolveRequestValue, Rulebricks

        client = Rulebricks(
            api_key="YOUR_API_KEY",
        )
        client.rules.parallel_solve(
            request={
                "eligibility": ParallelSolveRequestValue(
                    rule="1ef03ms",
                ),
                "offers": ParallelSolveRequestValue(
                    flow="OvmsYwn",
                ),
            },
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "parallel-solve",
            method="POST",
            json=convert_and_respect_annotation_metadata(
                object_=request, annotation=ParallelSolveRequest, direction="write"
            ),
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ParallelSolveResponse,
                    parse_obj_as(
                        type_=ParallelSolveResponse,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 400:
                raise BadRequestError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 500:
                raise InternalServerError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncRulesClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def solve(
        self,
        slug: str,
        *,
        request: DynamicRequestPayload,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> DynamicResponsePayload:
        """
        Executes a single rule identified by a unique slug. The request and response formats are dynamic, dependent on the rule configuration.

        Parameters
        ----------
        slug : str
            The unique identifier for the resource.

        request : DynamicRequestPayload

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        DynamicResponsePayload
            Rule execution successful. The response structure depends on the rule configuration.

        Examples
        --------
        import asyncio

        from rulebricks import AsyncRulebricks

        client = AsyncRulebricks(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.rules.solve(
                slug="slug",
                request={"name": "John Doe", "age": 30, "email": "jdoe@acme.co"},
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"solve/{jsonable_encoder(slug)}",
            method="POST",
            json=request,
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    DynamicResponsePayload,
                    parse_obj_as(
                        type_=DynamicResponsePayload,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 400:
                raise BadRequestError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 500:
                raise InternalServerError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def bulk_solve(
        self,
        slug: str,
        *,
        request: typing.Sequence[DynamicRequestPayload],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[BulkRuleResponseItem]:
        """
        Executes a particular rule against multiple request data payloads provided in a list.

        Parameters
        ----------
        slug : str
            The unique identifier for the resource.

        request : typing.Sequence[DynamicRequestPayload]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[BulkRuleResponseItem]
            Bulk rule execution successful. The response is an array of results, each dependent on the rule configuration.

        Examples
        --------
        import asyncio

        from rulebricks import AsyncRulebricks

        client = AsyncRulebricks(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.rules.bulk_solve(
                slug="slug",
                request=[
                    {"name": "John Doe", "age": 30, "email": "jdoe@acme.co"},
                    {"name": "Jane Doe", "age": 28, "email": "jane@example.com"},
                ],
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"bulk-solve/{jsonable_encoder(slug)}",
            method="POST",
            json=request,
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[BulkRuleResponseItem],
                    parse_obj_as(
                        type_=typing.List[BulkRuleResponseItem],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 400:
                raise BadRequestError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 500:
                raise InternalServerError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def parallel_solve(
        self,
        *,
        request: ParallelSolveRequest,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ParallelSolveResponse:
        """
        Executes multiple rules or flows in parallel based on a provided mapping of rule/flow slugs to payloads.

        Parameters
        ----------
        request : ParallelSolveRequest

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ParallelSolveResponse
            Parallel execution successful. The response is an object mirroring the request structure, but providing each rule/flow's results instead.

        Examples
        --------
        import asyncio

        from rulebricks import AsyncRulebricks, ParallelSolveRequestValue

        client = AsyncRulebricks(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.rules.parallel_solve(
                request={
                    "eligibility": ParallelSolveRequestValue(
                        rule="1ef03ms",
                    ),
                    "offers": ParallelSolveRequestValue(
                        flow="OvmsYwn",
                    ),
                },
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "parallel-solve",
            method="POST",
            json=convert_and_respect_annotation_metadata(
                object_=request, annotation=ParallelSolveRequest, direction="write"
            ),
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ParallelSolveResponse,
                    parse_obj_as(
                        type_=ParallelSolveResponse,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 400:
                raise BadRequestError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 500:
                raise InternalServerError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
