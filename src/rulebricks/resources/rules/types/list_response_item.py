# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from .list_response_item_request_schema_item import ListResponseItemRequestSchemaItem
from .list_response_item_response_schema_item import ListResponseItemResponseSchemaItem

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class ListResponseItem(pydantic.BaseModel):
    id: typing.Optional[str] = pydantic.Field(description="The unique identifier for the rule.")
    name: typing.Optional[str] = pydantic.Field(description="The name of the rule.")
    description: typing.Optional[str] = pydantic.Field(description="The description of the rule.")
    created_at: typing.Optional[str] = pydantic.Field(description="The creation date of the rule.")
    slug: typing.Optional[str] = pydantic.Field(description="The unique slug for the rule used in API requests.")
    request_schema: typing.Optional[typing.List[ListResponseItemRequestSchemaItem]]
    response_schema: typing.Optional[typing.List[ListResponseItemResponseSchemaItem]]

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        smart_union = True
        json_encoders = {dt.datetime: serialize_datetime}
